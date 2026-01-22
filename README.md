# 🍽️ Lunch Tracker

A simple, collaborative repository to track **where we go for lunch**.

This repo helps us:

* Remember places we’ve already tried
* Avoid eating the same thing every day
* Share recommendations and notes
* Decide where to go next more easily

You can see a preview of the map here: https://nsushant.github.io/ANT_OR_Lunch_Visits/lunch_map.html 
Double click an image to view in full size.

**Features:**
- 🗺️ Interactive map with all lunch locations
- 🗳️ Vote for your favorite restaurants
- 🏆 View rankings based on community votes
- 📸 Photo galleries for each location 

---

## 📌 What This Repo Is For

We use this repository to log:

* Lunch locations (restaurants, food trucks, cafeterias, etc.)
* Dates visited
* Who went
* Quick notes (price, wait time, what was good, what wasn’t)

It’s intentionally lightweight and low-maintenance.

---

## 📂 Repository Structure

```
.
├── lunch_log.md      # Main log of lunch visits / reviews
├── places.md         # Master list of lunch spots visited before
├── wishlist.md       # Places we want to try but nobody has visited
├── lunch_map.html    # Interactive map of lunch locations
├── ranking.html      # Restaurant rankings based on votes
└── README.md         # You are here
```

---

## 🗳️ Voting System

We've added an interactive voting system to help decide where to go!

**How to Vote:**
1. Open `lunch_map.html` in your browser
2. Enter your name to access the map
3. Click on any restaurant marker
4. Click the **"🗳️ Vote"** button
5. Give it a rank: 1, 2, or 3

**Point System:**
- **Rank 1** = 3 points 🥇
- **Rank 2** = 2 points 🥈
- **Rank 3** = 1 point 🥉

**Rules:**
- Each rank can only be used once (you can vote for max 3 restaurants)
- Each person can only vote once per restaurant
- Your votes are saved in your browser
- View all rankings on the **Rankings** page

**Managing Your Votes:**
- Click **"🗳️ My Votes"** on the rankings page to see your current votes
- You can **undo any vote** if you change your mind
- After undoing, that rank becomes available again for another restaurant

> **Note:** All votes are stored in `votes.json` and visible to everyone. Rankings update automatically!

---

## 📍 Adding a New Recommendation

If you'd like to recommend a place you've been to.

1. Add it to `places.md`
2. Include:

   * Name
   * Location
   * Cuisine
   * Price range
   * Note
   * pics

> Note 1: the price ranges are the following: 
> - \$:     > 10€
> - \$\$:   10€ - 15€
> - \$\$\$: < 15€

> Note 2: Give the exact location of the place (i.e., the address)

> Note 3: The pics field is optional. If you do give it, add you images in a subfolder of `\images` and put the relative path to this foler in the field pics.◊

Example: 
```md
---
- Name: Munji
- Location: Oude Koornmarkt 68, 2000 Antwerpen
- Cuisine: middle-eastern 
- Price range: $
- Note: Falafel place
- pics: images/munji
---
```
---


## 📝 Detailing a Visit 

This file stores metrics describing the experience after a visit. 
We use this data to decide the frequency of future recommendations for the visited place. 
If you'd like to detail your experience, 

1. Open `lunch_log.md`
2. Add a new entry at the **top** of the file
3. Use the following format:

```md
### YYYY-MM-DD — Restaurant Name
- **Location:** Area / Neighborhood
- **People:** @name1, @name2
- **Cost:** $ / $$ / $$$
- **Notes:** Short comments about the food, wait time, etc.
- **Rating out of 5:** 
```

Example:

```md
### 2025-01-15 — Tasty Noodles
- **Location:** Downtown
- **People:** Alice, Bob
- **Cost:** $$
- **Notes:** Fast service, great noodles, limited seating.
- **Rating out of 5:** 4
```

---

## ⭐ Wishlist

A list of places we'd like to try but no one has been to. 

Add it to `wishlist.md` with:

* Name
* Location
* Why it’s interesting

---

## 🤝 Contributing Guidelines

* Keep entries short and factual
* No need for perfect formatting — consistency > perfection
* Feel free to update old entries with better notes


---

## 🧠 Philosophy

> Tracking lunch is serious business.

But not *that* serious.

---

## 📄 License

This repository is for internal / casual use. No license specified unless added later.

Enjoy lunch! 🥪🌮🍜

