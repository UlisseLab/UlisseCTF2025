#include <string.h>
#include <stdlib.h>
#include <stdbool.h>
#include <stdio.h>
#include <unistd.h>
#include <sys/mman.h>

#define MAX_NOTE_LENGTH 500

typedef struct {
    long long int sender_balance;
    long long int amount;
    char* note;
} Transaction;

typedef struct {
    char* note;
    char* status;
} Result;

char* parse(const char* markdown) {
    if (!markdown) return NULL;

    size_t markdown_len = strlen(markdown);
    size_t html_capacity = markdown_len * 2 + 1;
    char *html = malloc(html_capacity);
    if (!html) return NULL;
    size_t pos = 0;

    for(size_t i = 0; i < markdown_len; i++){
        if(markdown[i] == 'n'){
            markdown_len = i;
            break;
        }
    }

    for (size_t i = 0; i < markdown_len && markdown[i] != '\n';) {
        if (markdown[i] == '*' && markdown[i + 1] == '*') {
            const char* openTag = "<b>";
            const char* closeTag = "</b>";
            size_t tagLen = strlen(openTag);
            memcpy(html + pos, openTag, tagLen);
            pos += tagLen;
            i += 2;

            while (i < markdown_len && !(markdown[i] == '*' && markdown[i + 1] == '*')) {
                html[pos++] = markdown[i++];
                if (pos >= html_capacity - 1) break;
            }
            if (i < markdown_len && markdown[i] == '*' && markdown[i + 1] == '*') {
                memcpy(html + pos, closeTag, strlen(closeTag));
                pos += strlen(closeTag);
                i += 2;
            }
        }
        else if (markdown[i] == '*') {
            const char* openTag = "<i>";
            const char* closeTag = "</i>";
            memcpy(html + pos, openTag, strlen(openTag));
            pos += strlen(openTag);
            i++;

            while (i < markdown_len && markdown[i] != '*') {
                html[pos++] = markdown[i++];
                if (pos >= html_capacity - 1) break;
            }
            if (i < markdown_len && markdown[i] == '*') {
                memcpy(html + pos, closeTag, strlen(closeTag));
                pos += strlen(closeTag);
                i++;
            }
        }
        else {
            html[pos++] = markdown[i++];
        }
        if (pos >= html_capacity - 1) {
            html_capacity *= 2;
            char *temp = realloc(html, html_capacity);
            if (!temp) {
                free(html);
                return NULL;
            }
            html = temp;
        }
    }

    html[pos] = '\0';
    return html;
}

Result handle_transaction(Transaction transaction, char* key) {
    char copy[MAX_NOTE_LENGTH] = { 0 };
    char* key_c = malloc(18);
    strcpy(key_c, key);
    strncpy(copy, transaction.note, MAX_NOTE_LENGTH-1);

    Result result = {};
    result.note = malloc(MAX_NOTE_LENGTH);
    result.status = malloc(16);
    strcpy(result.status, "error");
    if (transaction.sender_balance < transaction.amount) {
        return result;
    }
    if (transaction.amount <= 0) {
        return result;
    }

    char* note = parse(copy);
    if (note == NULL) {
        return result;
    }
    snprintf(result.note, MAX_NOTE_LENGTH-1, note);
    strcpy(result.status, "success");
    free(note);
    free(key_c);
    return result;
}