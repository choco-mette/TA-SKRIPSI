import re

class TextCleaner:
    @staticmethod
    def clean_text(text: str) -> str:
        """
        Membersihkan teks dari artefak PDF umum.
        """
        # 1. Ganti bullet point PDF aneh dengan standard dash
        # Simbol kotak "" sering muncul di PDF hasil convert Word
        text = text.replace('', '-').replace('•', '-')

        # 2. Hapus multiple newline yang berlebihan (lebih dari 2)
        # Sering terjadi karena layout halaman kosong
        text = re.sub(r'\n{3,}', '\n\n', text)

        # 3. Gabungkan baris yang terputus di tengah kalimat (opsional, hati-hati)
        # PDF sering memutus kalimat di akhir baris visual
        # Strategi aman: Hapus spasi di awal/akhir baris
        lines = [line.strip() for line in text.split('\n')]
        
        # 4. Filter baris yang terlalu pendek (kemungkinan nomor halaman atau footer noise)
        lines = [line for line in lines if len(line) > 1 or line == ''] # Keep empty lines for paragraph separation

        # Gabungkan kembali
        cleaned_text = '\n'.join(lines)

        # 5. Hapus spasi ganda
        cleaned_text = re.sub(r' +', ' ', cleaned_text)

        return cleaned_text.strip()
