/*
 * hle_misc.c - small replacements, and the reset of all of them.
 */
#include "runtime/recomp.h"
#include "runtime/runtime.h"
#include "runtime/bios.h"
#include "runtime/kanji.h"

void hle_gpu_reset(void);
void hle_cd_reset(void);

/* LIBGTE's InitGeom() patches the BIOS's exception handler for the GTE;
 * there is no BIOS code in memory to patch. */
void hle__patch_gte(void)
{
}

void hle_reset_all(void)
{
    bios_reset();
    kanji_reset();
    hle_gpu_reset();
    hle_cd_reset();
}
