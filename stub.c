#include <stdio.h>
#include <stdlib.h>
#include <string.h>
#include <windows.h>

// split markers so they don't appear as complete strings in .rdata
char MARKER1[] = {'F','U','S','E','D','_','_','S','T','A','R','T','_','_','1',0};
char MARKER2[] = {'F','U','S','E','D','_','_','S','T','A','R','T','_','_','2',0};
char MARKER3[] = {'F','U','S','E','D','_','_','E','N','D','_','_','_','_','_',0};

// find markers in the "fused_" program
char *find_marker(char *data, long size, const char *marker) {
    // get length of marker string
    int marker_len = strlen(marker);
    // go through every byte from END to START
    for (long i = size - marker_len; i >= 0; i--) {
        // find our marker and return the position
        if (memcmp(data + i, marker, marker_len) == 0) {
            // return a pointer to that specific position
            return data + i;
        }
    }
    return NULL;
}

int main() {
    // holds the self file path
    char self_path[MAX_PATH];
    GetModuleFileName(NULL, self_path, MAX_PATH); // find its own .exe path on disk with windows api call

    FILE *self = fopen(self_path, "rb"); // open itself as a regular file
    if (!self) {
        printf("Error: Could not open self\n");
        return 1;
    }

    fseek(self, 0, SEEK_END); // move to the end of the file
    long file_size = ftell(self);
    fseek(self, 0, SEEK_SET);

    // allocate memory based on the file size so its big enough to hold entire file
    char *data = malloc(file_size);
    fread(data, 1, file_size, self); // reads the entire file into RAM
    fclose(self); // close file

    // after allocating memory for "fused_" to be stored in memory file we start finding markers we placed inside pe binary

    char *m1 = find_marker(data, file_size, MARKER1);
    char *m2 = find_marker(data, file_size, MARKER2);
    char *m3 = find_marker(data, file_size, MARKER3);

    // check if all markers were found
    if (!m1 || !m2 || !m3) {
        printf("Error: Couldn't find embedded files\n");
        free(data);
        return 1;
    }

    int marker_len = strlen(MARKER1);
    
    char *app1_start = m1 + marker_len; // first byte of app1.exe
    long app1_size = m2 - app1_start;   // how many bytes is app1.exe

    char *app2_start = m2 + marker_len;
    long app2_size = m3 - app2_start;

    // get temp dir path
    char temp_path[MAX_PATH];
    GetTempPath(MAX_PATH, temp_path);

    char app1_temp[MAX_PATH];
    char app2_temp[MAX_PATH];
    snprintf(app1_temp, MAX_PATH, "%sapp1_temp.exe", temp_path);
    snprintf(app2_temp, MAX_PATH, "%sapp2_temp.exe", temp_path);

    // write app1 to temp file
    FILE *app1f = fopen(app1_temp, "wb");
    if (!app1f) {
        printf("Error: could not write app1 temp file\n");
        free(data);
        return 1;
    }
    fwrite(app1_start, 1, app1_size, app1f);
    fclose(app1f);

    // write app2 to temp file
    FILE *app2f = fopen(app2_temp, "wb");
    if (!app2f) {
        printf("Error: could not write app2 temp file\n");
        free(data);
        return 1;
    }
    fwrite(app2_start, 1, app2_size, app2f);
    fclose(app2f);

    // run app1 first, wait for it to finish
    system(app1_temp);

    char cmd[MAX_PATH + 20];
    snprintf(cmd, sizeof(cmd), "%s 1>&2", app2_temp);

    // run app2 with stderr redirection
    system(cmd);

    // clean up temp files
    remove(app1_temp);
    remove(app2_temp);

    free(data); // free memory
    return 0;
}