/*
 * hle_mcrd.c - LIBMCRD: the memory card.
 *
 * Sorcerer's Maze only starts the library (MemCardInit, MemCardStart) and
 * never reads or writes a card, so there is no card: every other function
 * logs its call and reports that no card is inserted.
 */
#include "runtime/recomp.h"
#include "runtime/runtime.h"
#include "psx/log.h"

#define MC_ERR_CARD_NOT_EXIST   1

void hle_MemCardInit(void)
{
}

void hle_MemCardEnd(void)
{
}

void hle_MemCardStart(void)
{
}

void hle_MemCardStop(void)
{
}

void hle_MemCardCallback(void)
{
    RETURN(0);
}

/* MemCardSync(mode, *cmds, *result): no command is waiting */
void hle_MemCardSync(void)
{
    RETURN(-1);
}

static void no_card(const char *function)
{
    psx_log("%s: no memory card (ra %08X)", function, GPR[31]);
    RETURN(MC_ERR_CARD_NOT_EXIST);
}

void hle_MemCardExist(void) { no_card("MemCardExist"); }
void hle_MemCardAccept(void) { no_card("MemCardAccept"); }
void hle_MemCardOpen(void) { no_card("MemCardOpen"); }
void hle_MemCardClose(void) { RETURN(0); }
void hle_MemCardReadData(void) { no_card("MemCardReadData"); }
void hle_MemCardWriteData(void) { no_card("MemCardWriteData"); }
void hle_MemCardReadFile(void) { no_card("MemCardReadFile"); }
void hle_MemCardWriteFile(void) { no_card("MemCardWriteFile"); }
void hle_MemCardGetDirentry(void) { no_card("MemCardGetDirentry"); }
void hle_MemCardCreateFile(void) { no_card("MemCardCreateFile"); }
void hle_MemCardFormat(void) { no_card("MemCardFormat"); }
