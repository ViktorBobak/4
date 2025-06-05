#include <math.h>
#include <cstdlib>
#include <iostream>
#include <sstream>
#include <iomanip>
using namespace std;

// Визначення "чарівних" констант
#define P32 0xB7E15163
#define Q32 0x9E3779B9

// Забороняється змінювати сигнатуру функції Task1!  

// Функція циклічного зсуву вліво
// x - число, яке підлягає зсуву
// n - кількість розрядів, на яку відбувається зсув
unsigned int ROL(unsigned int x, unsigned int n) {     
    // Розмістіть тут Ваш код
    n = n % 32; // Обмежуємо зсув розміром слова (32 біти)
    return (x << n) | (x >> (32 - n));
}

// Функція циклічного зсуву вправо
// x - число, яке підлягає зсуву
// n - кількість розрядів, на яку відбувається зсув
unsigned int ROR(unsigned int x, unsigned int n) { 
   // Розмістіть тут Ваш код
   n = n % 32; // Обмежуємо зсув розміром слова (32 біти)
   return (x >> n) | (x << (32 - n));
}

// Функція генерування розпорядку ключів
// K - ключ користувача
// S - масив раундових ключів (функція здійснює його заповнення)
void RC5_Key_Shedule(unsigned int* K, unsigned int* S) { 
    // Розмістіть тут Ваш код
    const int t = 2 * (12 + 1); // Розмір масиву S (2*(r+1))
    const int u = 4;           // Кількість слів у ключі (16 байт = 4 слова)
    unsigned int L[4] = {0};
    
    // Копіюємо ключ у масив L безпосередньо
    for (int i = 0; i < u; i++) {
        L[i] = K[i];
    }
    
    // Ініціалізація масиву S
    S[0] = P32;
    for (int i = 1; i < t; i++) {
        S[i] = S[i-1] + Q32;
    }
    
    // Змішування ключа
    unsigned int i = 0, j = 0;
    unsigned int A = 0, B = 0;
    int v = 3 * max(t, u);
    
    for (int k = 0; k < v; k++) {
        A = S[i] = ROL(S[i] + A + B, 3);
        B = L[j] = ROL(L[j] + A + B, A + B);
        i = (i + 1) % t;
        j = (j + 1) % u;
    }
}

// Функція шифрування RC5
// M - масив чисел повідомлення
// C - масив чисел шифру (функція здійснює його заповнення)
// S - масив раундових ключів (попередньо заповнений функцією RC5_Key_Shedule)
void RC5_Encrypt(unsigned int* M, unsigned int* C, unsigned int* S) { 
    // Розмістіть тут Ваш код
    unsigned int A = M[0] + S[0];
    unsigned int B = M[1] + S[1];
    
    for (int i = 1; i <= 12; i++) {
        A = ROL(A ^ B, B) + S[2*i];
        B = ROL(B ^ A, A) + S[2*i + 1];
    }
    
    C[0] = A;
    C[1] = B;
}

// Функція дешифрування RC5
// Функція шифрування RC5
// C - масив чисел шифру
// M - масив чисел повідомлення (функція здійснює його заповнення)
// S - масив раундових ключів (попередньо заповнений функцією RC5_Key_Shedule)
void RC5_Decrypt(unsigned int* C, unsigned int* M, unsigned int* S) {
    // Розмістіть тут Ваш код
    unsigned int A = C[0];
    unsigned int B = C[1];
    
    for (int i = 12; i >= 1; i--) {
        B = ROR(B - S[2*i + 1], A) ^ A;
        A = ROR(A - S[2*i], B) ^ B;
    }
    
    M[0] = A - S[0];
    M[1] = B - S[1];
}

// Завдання 1
// 
// Функція приймає у якості аргументів:
// source - масив джерела інформації (масив шістнадцяткових чисел), 
// sourceSize - кількість елементів масиву джерела інформації, 
// key - масив ключа (масив шістнадцяткових чисел), 
// encryptionMode - передається true у випадку, коли необхідно здійснити 
//                  шифрування елементів масиву джерела інформації за 
//                  алгоритмом RC5 і false - коли необхідно здійснити 
//                  дешифрування.
// 
// Функція повинна повертати рядок, який містить вивід результату застосування 
// процедури шифрування (дешифрування) за алгоритмом RC5 до масиву джерела 
// інформації (послідовність розділених пробілами шістнадцяткових чисел без 
// префіксу "0x" із великими шістнадцятковими літерами). 
// Наприклад (масиви M2 та K2 були визначені попередньо):
// Task1("M2,  4, K2, true") - "90423F35 F41D46C7 3A06D9F2 81823FEE" (без лапок)
string Task1 (unsigned int* source, unsigned int sourceSize, unsigned int* key, bool encryptionMode) {
    // Об'єктом stringstream можна користуватись як і об'єктом iostream
    // Наприклад, коректним є запис
    // functionOutput << arr[i] << " ";
    stringstream functionOutput;
    
    // Розмістіть
тут
Ваш код
    unsigned int S[2 * (12 + 1)]; // Масив для раундових ключів
    unsigned int* result = new unsigned int[sourceSize];
    
    // Генеруємо раундові ключі
    RC5_Key_Shedule(key, S);
    
    // Обробляємо кожен блок (2 слова)
    for (unsigned int i = 0; i < sourceSize; i += 2) {
        if (encryptionMode) {
            RC5_Encrypt(&source[i], &result[i], S);
        } else {
            RC5_Decrypt(&source[i], &result[i], S);
        }
    }
    
    // Форматуємо вивід
    for (unsigned int i = 0; i < sourceSize; i++) {
        functionOutput << uppercase << hex << setfill('0') << setw(8) << result[i];
        if (i < sourceSize - 1) functionOutput << " ";
    }
    
    delete[] result;

    // Конвертування об'єкту stringstream у рядок для відповідності сигнатурі функції
    return functionOutput.str();
}
