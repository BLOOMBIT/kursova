import requests
from bs4 import BeautifulSoup
import urllib.parse
import matplotlib
matplotlib.use('TkAgg')
import matplotlib.pyplot as plt
import re


def get_first_product_url(query):
    search_url = f"https://podorozhnyk.ua/ru/search/?query={urllib.parse.quote(query)}"
    headers = {"User-Agent": "Mozilla/5.0"}
    response = requests.get(search_url, headers=headers)
    soup = BeautifulSoup(response.text, 'html.parser')

    product_link_tag = soup.select_one('div.product-card__preview a')
    if product_link_tag:
        return urllib.parse.urljoin("https://podorozhnyk.ua", product_link_tag['href'])
    return None


def get_reviews_distribution(product_url):
    reviews_url = product_url.rstrip('/') + "/reviews/"
    headers = {"User-Agent": "Mozilla/5.0"}
    response = requests.get(reviews_url, headers=headers)
    soup = BeautifulSoup(response.content, 'html.parser')

    rating_counts = {str(i): 0 for i in range(1, 6)}
    rating_blocks = soup.select('div.ratings__item')

    for block in rating_blocks:
        stars = block.get("data-max-rating")
        count_tag = block.select_one("div.item__comments-count")
        if stars and count_tag:
            match = re.search(r'\d+', count_tag.text)
            count = int(match.group()) if match else 0
            rating_counts[stars] = count

    return rating_counts, reviews_url


def visualize_all_in_one(rating_counts):
    stars = sorted(rating_counts.keys(), reverse=True)
    counts = [rating_counts[star] for star in stars]
    total_reviews = sum(counts)

    # Индекс эффективности
    if total_reviews > 0:
        weighted_sum = sum(int(star) * count for star, count in rating_counts.items())
        index = (weighted_sum / total_reviews) * 20
    else:
        index = 0

    # Создание подграфиков
    fig, axs = plt.subplots(1, 3, figsize=(18, 5))
    fig.suptitle("Аналіз відгуків за препаратом", fontsize=16)

    # Гістограма
    axs[0].bar(stars, counts, color='skyblue')
    axs[0].set_title("Розподіл відгуків (зірки)")
    axs[0].set_xlabel("Кількість зірок")
    axs[0].set_ylabel("Кількість")
    axs[0].grid(axis='y')

    # Кругова діаграма
    axs[1].pie(counts, labels=[f"{star}" for star in stars], autopct='%1.1f%%', startangle=140)
    axs[1].set_title("Кругова діаграма відгуків")
    axs[1].axis('equal')

    # Індекс ефективності
    axs[2].bar(['Індекс ефективності'], [index], color='green')
    axs[2].set_ylim(0, 100)
    axs[2].set_ylabel("Бали зі 100")
    axs[2].set_title("Оцінка ефективності")

    plt.tight_layout()
    plt.subplots_adjust(top=0.85)
    plt.show()


def main():
    drug = input("Введи назву препарату: ").strip()
    product_url = get_first_product_url(drug)
    if product_url:
        print(f"\n🔗 Знайдено товар: {product_url}")
        rating_counts, reviews_url = get_reviews_distribution(product_url)
        print(f"💬 Посилання на відгуки: {reviews_url}")
        total = sum(rating_counts.values())
        if total == 0:
            print("❌ Немає відгуків або не вдалося витягнути дані.")
        else:
            for star, count in sorted(rating_counts.items(), reverse=True):
                print(f"{star} ⭐ — {count} відгуків")
            visualize_all_in_one(rating_counts)
    else:
        print("❌ Препарат не знайдено.")


main()


