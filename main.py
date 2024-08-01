import json
import openai

openai_api_key = "sk-proj-VjZIdxuFxU7zfOfjzxHKT3BlbkFJA5TsWBP3wZolnIajfhBP"
client = openai.OpenAI(api_key=openai_api_key)

def question_answer(question):
    print("Çeviri yapılıyor")

    try:
        response = client.chat.completions.create(
            messages=[
                {"role": "user", "content": question},
            ],
            model="gpt-3.5-turbo",
        )
        return response.choices[0].message.content
    except Exception as e:
        print(f"Error in question_answer: {e}")
        return None

languages = ["Azeri", "Uzbek", "Turkish", "Kazakh", "Kyrgyz"]
country_codes = ["az", "uz", "tr", "kz", "kg"]
dictList = [
    {
 "code": "az",
    "language": "Azeri",
},
 {
    "country_code": "uz",
    "language": "Uzbek",
 },
    {
        "country_code": "tr",
        "language": "Turkish",

    },

    {
        "country_code" : "kz",
        "language":"Kazakh",
    },
    {
        "country_code":"kg",
        "language":"Kyrgyz",
    }


]

file_name = 'en.json'

try:
    with open(file_name, 'r', encoding="utf-8") as dosya:
        question = dosya.read()

    sozluk = json.loads(question)
    texts = sozluk.get("texts", {})
    chunk_size = 10
    chunks = [dict(list(texts.items())[i:i + chunk_size]) for i in range(0, len(texts), chunk_size)]

    for index, language in enumerate(languages):
        translated_chunks = []
        country_code = country_codes[index]

        for i, chunk in enumerate(chunks):
            print(f"Chunk {i + 1} for language {language}: {len(chunk)} items")
            eklenecek_satir = f"Could you fill the values with translating them to {language}. However, be careful about that the response shouldn't have any explanation. Just give me the json response. Please keep each key on one line. Can you give me the answer in json format?"

            questionn = json.dumps(chunk) + " " + eklenecek_satir
            response = question_answer(questionn)

            if response:
                try:
                    translated_chunk = json.loads(response)
                    translated_chunks.append(translated_chunk)

                    print(f"Translated Chunk {i + 1} for language {language}:")
                    print(json.dumps(translated_chunk, indent=2, ensure_ascii=False))
                    print()
                except json.JSONDecodeError as e:
                    print(f"Error parsing JSON response for Chunk {i + 1} in language {language}: {e}")
                    continue

        output_file_name = f'{country_code}.json'
        with open(output_file_name, 'w', encoding='utf-8') as dosya:
            json.dump({"texts": {k: v for chunk in translated_chunks for k, v in chunk.items()}}, dosya, ensure_ascii=False, indent=2)

        print(f"Translations saved to {output_file_name}.")

except FileNotFoundError:
    print(f"{file_name} not found.")
except Exception as e:
    print(f"An error occurred: {e}")

def missing_keys(source_file, target_languages):
    print("Eksik anahtarlar kontrol ediliyor")

    try:
        with open(source_file, 'r', encoding='utf-8') as file:
            en_data = json.load(file)
        en_texts = en_data.get("texts", {})
    except FileNotFoundError:
        print(f"{source_file} bulunamadı.")
        return
    except json.JSONDecodeError:
        print(f"{source_file} geçerli bir JSON dosyası değil.")
        return

    language_to_country_code = {d["language"]: d["country_code"] for d in dictList}

    for language in target_languages:
        country_code = language_to_country_code.get(language)
        if not country_code:
            print(f"{language} dili için ülke kodu bulunamadı.")
            continue

        istenen_dosya = f'{country_code}.json'

        try:
            with open(istenen_dosya, 'r', encoding='utf-8') as file:
                translated_chunks = json.load(file).get("texts", {})
        except FileNotFoundError:
            translated_chunks = {}
            print(f"{istenen_dosya} bulunamadı.")

        missing_keys = set(en_texts.keys()) - set(translated_chunks.keys())

        while missing_keys:
            print(f"{language} dili için eksik anahtarlar bulundu: {missing_keys}")

            missing_texts = {key: en_texts[key] for key in missing_keys}
            translation_request = json.dumps(missing_texts) +  f"Could you fill the values with translating them to {language}. However, be careful about that the response shouldn't have any explanation. Just give me the json response. Please keep each key on one line. Can you give me the answer in json format?"

            response = question_answer(translation_request)

            if response:
                try:
                    translated_missing_texts = json.loads(response)
                    translated_chunks.update(translated_missing_texts)

                    with open(istenen_dosya, 'w', encoding='utf-8') as file:
                        json.dump({"texts": translated_chunks}, file, ensure_ascii=False, indent=2)

                    print(f"{language} dili için eksik anahtarlar çevrildi ve {istenen_dosya} güncellendi.")
                except json.JSONDecodeError:
                    print(f"Yanıt JSON formatında geçerli değil: {language}.")

                missing_keys = set(en_texts.keys()) - set(translated_chunks.keys())
            else:
                print(f"Çeviri için hata oluştu: {language}")
                break
        else:
            print(f"{language} dili için eksik anahtar bulunamadı.")

source_file = 'en.json'
missing_keys(source_file, languages)

