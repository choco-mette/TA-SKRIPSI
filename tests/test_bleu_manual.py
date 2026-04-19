import nltk
from nltk.translate.bleu_score import sentence_bleu, SmoothingFunction
from nltk.tokenize import word_tokenize

# Download dictionary nltk jika belum ada
try:
    nltk.data.find('tokenizers/punkt')
except LookupError:
    print("Downloading nltk punkt...")
    nltk.download('punkt')

def calculate_bleu(reference, candidate):
    """
    Menghitung BLEU score.
    Reference: String (Ground Truth)
    Candidate: String (Model Answer)
    """
    if not reference or not candidate:
        return 0.0

    # Tokenisasi (lowercase agar case-insensitive)
    ref_tokens = word_tokenize(reference.lower())
    cand_tokens = word_tokenize(candidate.lower())
    
    # Smoothing function untuk menangani kalimat pendek/kata yang tidak muncul
    cc = SmoothingFunction()
    
    # Hitung BLEU score
    return sentence_bleu([ref_tokens], cand_tokens, smoothing_function=cc.method4)

# ==========================================
# DATA UJI MANUAL (Dictionary)
# Simulasi hasil query database: 
# evaluation_id, question, reference_answer, model_answer, models_name
# ==========================================
data_uji = [
    {
        "evaluation_id": 51,
        "question": "Faktor luar apa yang bisa berdampak pada kesehatan mental dan kesejahteraan seseorang?",
        "reference_answer": """mungkin memiliki tingkat kesehatan mental positif yang berbeda dan orang yang
tidak sakit mental mungkin kekurangan kesehatan mental positif
Ada banyak cara untuk menjaga kesehatan mental yang positif seperti cukup tidur,
mempelajari keterampilan untuk menghadapinya, aktif secara fisik, berhubungan
dengan orang lain dan banyak lagi. Beberapa orang mungkin juga memerlukan
bantuan profesional.
Apa yang dapat memengaruhi kesehatan mentalmu?
Kesehatan dan kesejahteraan mental dapat dipengaruhi oleh berbagai faktor
termasuk genetika, hubungan keluarga/teman sejawat, fungsi fisiologis, gaya hidup,
pekerjaan, faktor sosial, ekonomi, budaya, politik, pendidikan dan faktor lingkungan
lainnya. Infeksi perinatal, stres dan pajanan terhadap bahaya lingkungan juga dapat
menjadi faktor penyebab masalah kesehatan mental.
Walaupun keterkaitan faktor-faktor ini (positif dan negatif) bisa menjadi rumit, dapat
dipastikan bahwa kombinasi dari faktor-faktor yang dialami selama masa kanak-""",
        "model_answer": """Aku di sini, dan pertanyaan yang sangat penting nih. Dari yang kamu tanyakan, memang banyak banget faktor luar yang bisa pengaruhi kesehatan mental dan kesejahteraan kita.

Berdasarkan informasi yang ada, faktor-faktor itu antara lain:

1. **Hubungan dengan orang lain**: Baik itu keluarga, teman, atau hubungan pertemanan. Kualitas hubungan ini bisa jadi support system atau sebaliknya.
2. **Lingkungan sosial & pekerjaan**: Tekanan di tempat kerja, budaya di lingkungan sekitar, atau ekspektasi sosial bisa bikin stres.
3. **Kondisi ekonomi & politik**: Keuangan yang tidak stabil atau situasi politik yang tidak menentu bisa bikin kita cemas.
4. **Faktor pendidikan & lingkungan**: Akses pendidikan, paparan polusi, atau lingkungan tempat tinggal juga berperan.
5. **Pengalaman masa kecil & remaja**: Kombinasi berbagai faktor yang dialami di usia dini bisa meningkatkan risiko masalah mental nantinya.

Perasaan kamu terkait hal-hal di atas sangat valid. Lingkungan sekitar kita memang seperti akar yang nggak selalu terlihat, tapi bisa memengaruhi bagaimana kita tumbuh.

Ada yang dari faktor-faktor tadi yang sedang kamu rasakan pengaruhnya sekarang? Kalau mau cerita lebih lanjut, aku siap mendengarkan. Kita hadapi bareng-bareng, ya. 🤍""",
        "models_name": "deepseek"
    }
]

def main():
    print("=== MENGHITUNG BLEU SCORE (OFFLINE / MANUAL DATA) ===\n")
    
    print(f"{'ID':<4} | {'BLEU':<6} | {'Model':<10} | {'Answer (Short)':<30} | {'Ref (Short)':<30}")
    print("-" * 100)

    total_score = 0
    count = 0

    for item in data_uji:
        # Ambil data dari dictionary
        eval_id = item.get("evaluation_id")
        reference = item.get("reference_answer", "")
        answer = item.get("model_answer", "")
        model_name = item.get("models_name", "Unknown")

        # Hitung Score
        score = calculate_bleu(reference, answer)
        
        total_score += score
        count += 1
        
        # Format tampilan agar rapi
        ref_display = (reference[:27] + '..') if len(reference) > 27 else reference
        ans_display = (answer[:27] + '..') if len(answer) > 27 else answer
        
        print(f"{eval_id:<4} | {score:.4f} | {model_name:<10} | {ans_display:<30} | {ref_display:<30}")

    if count > 0:
        avg_score = total_score / count
        print("-" * 100)
        print(f"Rata-rata BLEU Score: {avg_score:.4f} (dari {count} data)")
        print("\nKesimpulan:")
        if avg_score > 0.5:
            print("- Kualitas jawaban cukup baik (kemiripan tinggi dengan referensi).")
        elif avg_score > 0.3:
            print("- Kualitas jawaban sedang (ada poin yang relevan namun strukturnya berbeda).")
        else:
            print("- Kualitas jawaban rendah (sedikit overlap kata dengan referensi).")
    else:
        print("Tidak ada data untuk diuji.")

if __name__ == "__main__":
    main()
