/*
 * 函数指针样例 - Function Pointer Example
 * 用于测试间接调用和函数指针的解析
 */

#include <stdio.h>

/* 比较函数类型定义 */
typedef int (*CompareFunc)(const void*, const void*);

/* 整数比较函数 */
int compare_int(const void* a, const void* b) {
    int ia = *(const int*)a;
    int ib = *(const int*)b;
    return ia - ib;
}

/* 字符串比较函数 */
int compare_string(const void* a, const void* b) {
    const char* sa = (const char*)a;
    const char* sb = (const char*)b;
    return strcmp(sa, sb);
}

/* 通用排序函数 - 使用函数指针 */
void sort_array(void* base, int count, int size, CompareFunc cmp) {
    char* arr = (char*)base;
    char temp[256];

    for (int i = 0; i < count - 1; i++) {
        for (int j = 0; j < count - i - 1; j++) {
            void* elem1 = arr + j * size;
            void* elem2 = arr + (j + 1) * size;

            if (cmp(elem1, elem2) > 0) {
                /* 交换元素 */
                memcpy(temp, elem1, size);
                memcpy(elem1, elem2, size);
                memcpy(elem2, temp, size);
            }
        }
    }
}

/* 整数数组排序入口 */
void sort_int_array(int* arr, int count) {
    sort_array(arr, count, sizeof(int), compare_int);
}

/* 字符串数组排序入口 */
void sort_string_array(char** arr, int count) {
    sort_array(arr, count, sizeof(char*), compare_string);
}
