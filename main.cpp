import java.nio.ByteBuffer;
import java.nio.charset.StandardCharsets;

public class RC5Cipher {

    private static final int W = 32;      // word size in bits
    private static final int R = 12;      // number of rounds
    private static final int B = 16;      // key size in bytes
    private static final int C = B / 4;   // key size in 32-bit words
    private static final int T = 2 * (R + 1); // size of S-array

    private static final int P32 = 0xB7E15163;
    private static final int Q32 = 0x9E3779B9;

    public static String Task1(int[] source, int sourceSize, int[] key, boolean encryptionMode) {
        int[] S = keyExpansion(key);
        int[] result = new int[sourceSize];

        for (int i = 0; i < sourceSize; i += 2) {
            int A = source[i];
            int B = source[i + 1];

            if (encryptionMode) {
                A += S[0];
                B += S[1];
                for (int j = 1; j <= R; j++) {
                    A = Integer.rotateLeft(A ^ B, B) + S[2 * j];
                    B = Integer.rotateLeft(B ^ A, A) + S[2 * j + 1];
                }
            } else {
                for (int j = R; j >= 1; j--) {
                    B = Integer.rotateRight(B - S[2 * j + 1], A) ^ A;
                    A = Integer.rotateRight(A - S[2 * j], B) ^ B;
                }
                B -= S[1];
                A -= S[0];
            }

            result[i] = A;
            result[i + 1] = B;
        }

        StringBuilder sb = new StringBuilder();
        for (int i = 0; i < sourceSize; i++) {
            sb.append(String.format("%08X", result[i]));
            if (i < sourceSize - 1) sb.append(" ");
        }
        return sb.toString();
    }

    private static int[] keyExpansion(int[] key) {
        int[] S = new int[T];
        S[0] = P32;
        for (int i = 1; i < T; i++) {
            S[i] = S[i - 1] + Q32;
        }

        int[] L = new int[C];
        System.arraycopy(key, 0, L, 0, key.length);

        int A = 0, B = 0, i = 0, j = 0;
        for (int k = 0; k < 3 * Math.max(C, T); k++) {
            A = S[i] = Integer.rotateLeft(S[i] + A + B, 3);
            B = L[j] = Integer.rotateLeft(L[j] + A + B, A + B);
            i = (i + 1) % T;
            j = (j + 1) % C;
        }
        return S;
    }

    public static void main(String[] args) {
        // Новий текст для шифрування
        String text = "Чорний Джек 2025!";
        byte[] bytes = text.getBytes(StandardCharsets.UTF_8);

        // Додати padding до кратності 8 байтам (2 int)
        int paddedLength = (bytes.length + 7) / 8 * 8;
        byte[] padded = new byte[paddedLength];
        System.arraycopy(bytes, 0, padded, 0, bytes.length);

        // Перетворення в int-масив
        int[] source = new int[padded.length / 4];
        for (int i = 0; i < source.length; i++) {
            source[i] = ByteBuffer.wrap(padded, i * 4, 4).getInt();
        }

        // Новий ключ (4 слова по 32 біти)
        int[] key = {
                0x0F1E2D3C, 0x4B5A6978,
                0x8796A5B4, 0xC3D2E1F0
        };

        String encrypted = Task1(source, source.length, key, true);
        System.out.println("Encrypted: " + encrypted);

        // Парсинг назад у масив
        String[] parts = encrypted.split(" ");
        int[] encryptedInts = new int[parts.length];
        for (int i = 0; i < parts.length; i++) {
            encryptedInts[i] = (int) Long.parseLong(parts[i], 16);
        }

        String decryptedHex = Task1(encryptedInts, encryptedInts.length, key, false);
        int[] decryptedInts = new int[encryptedInts.length];
        String[] hexParts = decryptedHex.split(" ");
        for (int i = 0; i < hexParts.length; i++) {
            decryptedInts[i] = (int) Long.parseLong(hexParts[i], 16);
        }

        // Перетворення назад у байти
        byte[] decryptedBytes = new byte[decryptedInts.length * 4];
        for (int i = 0; i < decryptedInts.length; i++) {
            ByteBuffer.wrap(decryptedBytes, i * 4, 4).putInt(decryptedInts[i]);
        }
        String resultText = new String(decryptedBytes, StandardCharsets.UTF_8).trim();
        System.out.println("Decrypted: " + resultText);
    }
}
