/*
 * disc.h - the player's own disc image (.bin/.cue, .chd or .iso) and its
 * ISO9660 file system.  Nothing of the game is shipped with the port: all
 * data is read from here.
 */
#ifndef DISC_DISC_H
#define DISC_DISC_H

#include <stdint.h>

#ifdef __cplusplus
extern "C" {
#endif

#define DISC_SECTOR_DATA        2048    /* user data of a Mode 1 / Mode 2 Form 1 sector */

/* disc_check() result */
enum DiscStatus {
    DISC_NONE = 0,                  /* nothing chosen */
    DISC_UNREADABLE,                /* not a disc image we can read */
    DISC_WRONG_GAME,                /* a PS1 disc, but not Sorcerer's Maze (USA) */
    DISC_OTHER_DUMP,                /* Sorcerer's Maze, but other executables than the port's */
    DISC_OK                         /* the executables match the recompiled code */
};

/* Opens a .bin/.cue/.chd/.iso; FALSE if it cannot be read. */
int disc_open(const char *path);
void disc_close(void);

/* Reads `count` sectors of user data starting at `lba`. */
int disc_read_sectors(uint32_t lba, uint32_t count, void *out);

/* Finds a file ("\\DATA\\GAME.PAK;1", case and ";1" optional). */
int disc_find_file(const char *path, uint32_t *lba, uint32_t *size);

/* Opens the image and checks that it is Sorcerer's Maze (USA) with the
 * executables the port was recompiled from.  `detail` gets a short
 * explanation (UTF-8). */
int disc_check(const char *path, char *detail, int detail_size);

/* (game_check.c) the second half of disc_check(): the opened disc's
 * executables against the recompiled code; a DiscStatus */
int disc_check_executables(char *detail, int detail_size);

/* A file of the opened disc, whole; FALSE if it is missing or larger than `size`. */
int disc_read_file(const char *path, void *out, uint32_t size, uint32_t *length);

/* Total sectors of the opened image. */
uint32_t disc_sector_count(void);

#ifdef __cplusplus
}
#endif

#endif /* DISC_DISC_H */
