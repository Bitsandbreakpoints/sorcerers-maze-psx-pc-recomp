/*
 * hle_cd.c - LIBCD: the CD-ROM, read from the player's disc image
 * (src/disc/).  Reads finish at once: CdRead() copies the sectors into
 * PS1 memory and CdReadSync() reports completion.
 */
#include <stdio.h>
#include <string.h>
#include "runtime/recomp.h"
#include "runtime/runtime.h"
#include "disc/disc.h"
#include "psx/log.h"

/* sectors before LBA 0: the 2 second pregap (00:02:00) */
#define PREGAP_SECTORS          150
#define SECTORS_PER_SECOND      75

/* CdControl() commands */
#define CDL_NOP                 0x01
#define CDL_SETLOC              0x02
#define CDL_READN               0x06
#define CDL_STOP                0x08
#define CDL_PAUSE               0x09
#define CDL_SETMODE             0x0E
#define CDL_GETLOCL             0x10
#define CDL_GETLOCP             0x11
#define CDL_GETTN               0x13
#define CDL_GETTD               0x14
#define CDL_SEEKL               0x15
#define CDL_SEEKP               0x16
#define CDL_READS               0x1B

#define STAT_MOTOR_ON           0x02
#define MODE_SIZE_MASK          0x30    /* CdlModeSize0/1: 2340-byte sectors */

/* CdlFILE: CdlLOC pos (4 bytes), u_long size, char name[16] */
#define FILE_POS                0
#define FILE_SIZE               4
#define FILE_NAME               8
#define FILE_NAME_SIZE          16

static int s_position;                  /* LBA of the next read (CdlSetloc) */
static int s_mode;
static uint32_t s_data_callback;

static int bcd_to_int(uint8_t bcd)
{
    return (bcd >> 4) * 10 + (bcd & 0xF);
}

static uint8_t int_to_bcd(int value)
{
    return (uint8_t) ((value / 10) << 4 | value % 10);
}

void hle_cd_reset(void)
{
    s_position = 0;
    s_mode = 0;
    s_data_callback = 0;
}

static int pos_to_int(uint32_t p)
{
    return (bcd_to_int((uint8_t) RD8(p)) * 60 + bcd_to_int((uint8_t) RD8(p + 1)))
               * SECTORS_PER_SECOND
           + bcd_to_int((uint8_t) RD8(p + 2)) - PREGAP_SECTORS;
}

static void int_to_pos(int lba, uint32_t p)
{
    lba += PREGAP_SECTORS;
    WR8(p, int_to_bcd(lba / (SECTORS_PER_SECOND * 60)));
    WR8(p + 1, int_to_bcd(lba / SECTORS_PER_SECOND % 60));
    WR8(p + 2, int_to_bcd(lba % SECTORS_PER_SECOND));
}

void hle_CdInit(void)
{
    hle_cd_reset();
    RETURN(1);
}

static void control(void)
{
    uint32_t com = GPR[4] & 0xFF, param = GPR[5], result = GPR[6];
    switch (com) {
    case CDL_SETLOC:
        if (param) {
            s_position = pos_to_int(param);
        }
        break;
    case CDL_SETMODE:
        if (param) {
            s_mode = RD8(param);
        }
        break;
    case CDL_READN:
    case CDL_READS:
        if (param) {
            s_position = pos_to_int(param);
        }
        psx_log("CdControl(%u): streaming reads are not supported", com);
        break;
    case CDL_GETLOCL:
    case CDL_GETLOCP:
        if (result) {
            int_to_pos(s_position, result + (com == CDL_GETLOCP ? 5 : 0));
        }
        break;
    case CDL_NOP:
    case CDL_STOP:
    case CDL_PAUSE:
    case CDL_SEEKL:
    case CDL_SEEKP:
        break;
    default:
        psx_log("CdControl(%u) ignored", com);
        break;
    }
    if (result && com != CDL_GETLOCL && com != CDL_GETLOCP) {
        WR8(result, STAT_MOTOR_ON);
    }
    RETURN(1);
}

void hle_CdControl(void)
{
    control();
}

void hle_CdControlF(void)
{
    control();
}

void hle_CdControlB(void)
{
    control();
}

void hle_CdRead(void)
{
    int sectors = (int) GPR[4];
    uint32_t buf = GPR[5];
    int mode = (int) GPR[6];
    if ((mode | s_mode) & MODE_SIZE_MASK) {
        psx_log("CdRead: mode %02X (2340-byte sectors) is not supported", mode);
    }
    for (int i = 0; i < sectors; i++) {
        void *p = rt_pointer(buf + (uint32_t) i * DISC_SECTOR_DATA);
        if (!p || !disc_read_sectors((uint32_t) s_position, 1, p)) {
            psx_log("CdRead: cannot read sector %d to %08X", s_position, buf);
            RETURN(0);
            return;
        }
        s_position++;
    }
    RETURN(1);
}

void hle_CdReadSync(void)
{
    if (GPR[5]) {
        WR8(GPR[5], STAT_MOTOR_ON);
    }
    RETURN(0);                          /* no sectors left: done */
}

void hle_CdReadBreak(void)
{
    RETURN(0);
}

void hle_CdDataCallback(void)
{
    uint32_t old = s_data_callback;
    s_data_callback = GPR[4];
    RETURN(old);
}

void hle_CdRead2(void)
{
    psx_log("CdRead2(%02X): streaming is not supported", GPR[4]);
    RETURN(1);
}

void hle_CdSearchFile(void)
{
    uint32_t fp = GPR[4], name_address = GPR[5];
    char name[64];
    uint32_t lba, size;
    int n = 0;
    while (n < (int) sizeof(name) - 1) {
        char c = (char) RD8(name_address + n);
        if (!c) {
            break;
        }
        name[n++] = c;
    }
    name[n] = 0;
    if (!disc_find_file(name, &lba, &size)) {
        psx_log("CdSearchFile: %s not found", name);
        RETURN(0);
        return;
    }
    int_to_pos((int) lba, fp + FILE_POS);
    WR8(fp + FILE_POS + 3, 0);
    WR32(fp + FILE_SIZE, size);
    /* the name without the directories */
    const char *base = name;
    for (const char *p = name; *p; p++) {
        if (*p == '\\' || *p == '/') {
            base = p + 1;
        }
    }
    for (int i = 0; i < FILE_NAME_SIZE; i++) {
        WR8(fp + FILE_NAME + i, i < (int) strlen(base) ? (uint8_t) base[i] : 0);
    }
    RETURN(fp);
}

/* CdSync(): every command finishes at once */
void hle_CdSync(void)
{
    if (GPR[5]) {
        WR8(GPR[5], STAT_MOTOR_ON);
    }
    RETURN(2);                          /* CdlComplete */
}

/* (only for streaming reads, which the game does not use) */
void hle_CdGetSector(void)
{
    psx_log("CdGetSector(%08X, %u): no sector is buffered", GPR[4], GPR[5]);
    RETURN(0);
}
