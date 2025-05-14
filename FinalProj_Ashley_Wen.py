"""
Project Gutenberg Book Search Tool - Final Project CIS 117
Author: Ashley Wen
Date: May 16, 2025

Search for books by title or URL from Project Gutenberg. Then, display the 10 most common words in a book.
Save the top 10 most common words and book title in a database.
"""

import sqlite3
import tkinter as tk
import requests

class BookSearch:
    """Run the book search tool and find the top ten words."""

    def __init__(self, window):
        """
        Set up the window for the application and connect to the database.
        """
        self.window = window
        self.window.title("Top 10 Words Look-up")

        # Set up the database for storing book data
        self.setup_database()

        # Create the user interface (buttons, fields, etc.)
        self.create_window()

    def setup_database(self):
        """
        Create a database to store book title and top 10 words.
        """
        try:
            # Connect to the books database
            self.db = sqlite3.connect("books.db")
            self.cursor = self.db.cursor()

            # Delete books table if it already exists and create a new one
            self.cursor.execute("DROP TABLE IF EXISTS books")

            # Create a new table with columns for the book title and 10 most common words. Format as word in column 1 and count in column 2 for top 10 words
            self.cursor.execute("""
                CREATE TABLE books (
                    title TEXT PRIMARY KEY,
                    word1 TEXT, count1 INTEGER,
                    word2 TEXT, count2 INTEGER,
                    word3 TEXT, count3 INTEGER,
                    word4 TEXT, count4 INTEGER,
                    word5 TEXT, count5 INTEGER,
                    word6 TEXT, count6 INTEGER,
                    word7 TEXT, count7 INTEGER,
                    word8 TEXT, count8 INTEGER,
                    word9 TEXT, count9 INTEGER,
                    word10 TEXT, count10 INTEGER
                )
            """)
            self.db.commit()
        except sqlite3.Error:
            self.show_message("Error setting up the database.")

    def create_window(self):
        """
        Create a GUI for text fields and buttons.
        """
        # Label and entry field for book title
        tk.Label(self.window, text="Book Title:").pack()
        self.title_field = tk.Entry(self.window)
        self.title_field.pack()

        # Button to search for a book by title
        tk.Button(self.window, text="Search", command=self.search_by_title).pack()

        # Label and entry field for the URL (optional)
        tk.Label(self.window, text="Book URL:").pack()
        self.url_field = tk.Entry(self.window)
        self.url_field.pack()

        # Button to search for a book by URL
        tk.Button(self.window, text="Search", command=self.search_by_url).pack()

        # Text area to show results (top 10 words)
        tk.Label(self.window, text="Top 10 Words:").pack()
        self.result_area = tk.Text(self.window)
        self.result_area.pack()

    def search_by_title(self):
        """
        Search for a book by its title in the database and display the top 10 words.
        """
        title = self.title_field.get().strip()
        if not title:
            self.result_area.delete(1.0, tk.END)
            self.result_area.insert(tk.END, "Enter a book title to search")
            return

        try:
            # Execute query to fetch book by title
            self.cursor.execute("SELECT * FROM books WHERE title = ?", (title,))
            book_data = self.cursor.fetchone()

            self.result_area.delete(1.0, tk.END)

            if book_data:
                # Display top 10 words if the book is found
                self.display_words(book_data)
            else:
                self.result_area.insert(tk.END, "Book not found in the database. Try searching by URL")
                
        except sqlite3.Error:
            # Show error if an issue occurs during database search
            self.result_area.delete(1.0, tk.END)
            self.result_area.insert(tk.END, "Error searching the database")

    def search_by_url(self):
        """
        Fetch a book from a URL, count the top 10 words, and save them to the database.
        """
        url = self.url_field.get().strip()
        title = self.title_field.get().strip()

        if not url:
            self.result_area.delete(1.0, tk.END)
            self.result_area.insert(tk.END, "Enter a URL to search")
            return

        try:
            # Send a GET request to fetch book text from the provided URL
            response = requests.get(url, timeout=10)
            response.raise_for_status()
            book_text = response.text

            # Count the frequency of words in the book text
            word_counts = self.count_words(book_text)

            # Sort the words by frequency and get the top 10
            top_words = sorted(word_counts.items(), key=lambda x: x[1], reverse=True)[:10]

            # Prepare data to insert into the database
            db_data = [title]
            for word, count in top_words:
                db_data.append(word)
                db_data.append(count)

            # Ensure the data has exactly 10 words and counts
            while len(db_data) < 21:
                db_data.append("")
                db_data.append(0)

            # Insert book data into the database (or replace if exists)
            self.cursor.execute("""
                INSERT OR REPLACE INTO books (
                    title, word1, count1, word2, count2, word3, count3, word4, count4,
                    word5, count5, word6, count6, word7, count7, word8, count8,
                    word9, count9, word10, count10
                ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
            """, db_data)
            self.db.commit()

            # Display top 10 words in the result area
            self.display_words(db_data)

        except requests.RequestException:
            self.result_area.insert(tk.END, "Error: Couldn't get the book from the URL")
        except sqlite3.Error:
            self.result_area.insert(tk.END, "Error while saving to the database")

    def count_words(self, text):
        """
        Count how many times each word appears in the given text
        """
        words = text.lower().split()  # Split the text into words and convert to lowercase
        word_counts = {}  # Make dictionary to store word counts

        for word in words:
            # Clean up the word by removing any special characters, non-letters, punctuation,
            clean_word = ''.join(char for char in word if char.isalnum())
            if clean_word:  # Count if word is not empty
                if clean_word in word_counts:
                    word_counts[clean_word] += 1  # Increase count if word already found
                else:
                    word_counts[clean_word] = 1  # Add new word to the dictionary

        return word_counts

    def display_words(self, data):
        """
        Display the top 10 words and their counts, 
        """
        for i in range(1, len(data), 2):  # Display words and their respective counts
            self.result_area.insert(tk.END, f"{data[i]}: {data[i+1]}\n")

def main():
    """Run the program and display the window."""
    window = tk.Tk()
    app = BookSearch(window)
    window.mainloop()

if __name__ == "__main__":
    main()
