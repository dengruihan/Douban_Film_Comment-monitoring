from bs4 import BeautifulSoup
import re


def parse_comments(html_text):
    soup = BeautifulSoup(html_text, "lxml")
    comment_items = soup.find_all("div", class_="comment-item")
    if not comment_items:
        return []
    comments = []
    for item in comment_items:
        comment_info = item.find("div", class_="comment-info")
        user_name = None
        if comment_info:
            first_a = comment_info.find("a")
            if first_a:
                user_name = first_a.get_text(strip=True)

        star_rating = None
        rating_span = item.find("span", class_=re.compile(r"rating"))
        if rating_span:
            class_attr = rating_span.get("class", [])
            for cls in class_attr:
                match = re.search(r"allstar(\d)0", cls)
                if match:
                    star_rating = int(match.group(1))
                    break

        short_span = item.find("span", class_="short")
        comment_text = short_span.get_text(strip=True) if short_span else ""

        votes_span = item.find("span", class_="votes")
        vote_count = int(votes_span.get_text(strip=True)) if votes_span else 0

        comment_time = None
        if comment_info:
            spans = comment_info.find_all("span")
            if spans:
                last_span = spans[-1]
                comment_time = last_span.get("title") or last_span.get_text(strip=True)

        comments.append({
            "user_name": user_name,
            "star_rating": star_rating,
            "comment_text": comment_text,
            "vote_count": vote_count,
            "comment_time": comment_time,
        })
    return comments


def parse_movie_info(html_text):
    soup = BeautifulSoup(html_text, "lxml")
    name_span = soup.find("span", property="v:itemreviewed")
    rating_span = soup.find("span", property="v:average")
    if not name_span or not rating_span:
        return None
    movie_name = name_span.get_text(strip=True)
    avg_rating = float(rating_span.get_text(strip=True))
    return {"movie_name": movie_name, "avg_rating": avg_rating}
