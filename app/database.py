import sqlite3
from datetime import datetime
import json
from pathlib import Path
from typing import Optional, Dict, Any
from app.schemas import ArticleStructure, ShortArticleStructure, MediumArticleStructure, LongArticleStructure

class ArticleDB:
    def __init__(self):
        db_path = Path(__file__).parent / "articles.db"
        self.conn = sqlite3.connect(str(db_path))
        self.conn.row_factory = sqlite3.Row
        self.create_tables()

    def create_tables(self):
        """Create the necessary tables if they don't exist"""
        with self.conn:
            # Main article table
            self.conn.execute('''
                CREATE TABLE IF NOT EXISTS articles (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    topic TEXT NOT NULL,
                    style TEXT NOT NULL,
                    title TEXT NOT NULL,
                    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                    intro_paragraphs TEXT,
                    conclusion_paragraphs TEXT
                )
            ''')

            # Main headings table
            self.conn.execute('''
                CREATE TABLE IF NOT EXISTS main_headings (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    article_id INTEGER,
                    title TEXT NOT NULL,
                    paragraphs TEXT,
                    position INTEGER NOT NULL,
                    FOREIGN KEY (article_id) REFERENCES articles (id)
                )
            ''')

            # Subheadings table
            self.conn.execute('''
                CREATE TABLE IF NOT EXISTS sub_headings (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    main_heading_id INTEGER,
                    title TEXT NOT NULL,
                    paragraphs TEXT,
                    position INTEGER NOT NULL,
                    FOREIGN KEY (main_heading_id) REFERENCES main_headings (id)
                )
            ''')

            # Sub-subheadings table
            self.conn.execute('''
                CREATE TABLE IF NOT EXISTS sub_sub_headings (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    sub_heading_id INTEGER,
                    title TEXT NOT NULL,
                    paragraphs TEXT,
                    position INTEGER NOT NULL,
                    FOREIGN KEY (sub_heading_id) REFERENCES sub_headings (id)
                )
            ''')

    def save_article(self, topic: str, style: str, article: ArticleStructure) -> int:
        """Save an article and return its ID"""
        with self.conn:
            # Insert main article
            cursor = self.conn.execute(
                '''INSERT INTO articles 
                   (topic, style, title, intro_paragraphs, conclusion_paragraphs)
                   VALUES (?, ?, ?, ?, ?)''',
                (topic, style, article.content.title,
                 json.dumps(article.content.intro_paragraphs) if hasattr(article.content, 'intro_paragraphs') else '[]',
                 json.dumps(article.content.conclusion_paragraphs) if hasattr(article.content, 'conclusion_paragraphs') else '[]')
            )
            article_id = cursor.lastrowid

            # Only process headings for medium and long articles
            if not isinstance(article.content, ShortArticleStructure):
                # Insert main headings
                for i, heading in enumerate(article.content.main_headings):
                    cursor = self.conn.execute(
                        '''INSERT INTO main_headings 
                           (article_id, title, paragraphs, position)
                           VALUES (?, ?, ?, ?)''',
                        (article_id, heading.title,
                         json.dumps(heading.paragraphs), i)
                    )
                    main_heading_id = cursor.lastrowid

                    # Insert subheadings
                    if heading.sub_headings:
                        for j, sub in enumerate(heading.sub_headings):
                            cursor = self.conn.execute(
                                '''INSERT INTO sub_headings 
                                   (main_heading_id, title, paragraphs, position)
                                   VALUES (?, ?, ?, ?)''',
                                (main_heading_id, sub.title,
                                 json.dumps(sub.paragraphs), j)
                            )
                            sub_heading_id = cursor.lastrowid

                            # Insert sub-subheadings
                            if sub.sub_headings:
                                for k, subsub in enumerate(sub.sub_headings):
                                    self.conn.execute(
                                        '''INSERT INTO sub_sub_headings 
                                           (sub_heading_id, title, paragraphs, position)
                                           VALUES (?, ?, ?, ?)''',
                                        (sub_heading_id, subsub.title,
                                         json.dumps(subsub.paragraphs), k)
                                    )

        return article_id

    def get_article_list(self):
        """Get a list of all articles with basic info"""
        cursor = self.conn.execute('''
            SELECT id, topic, style, title, created_at
            FROM articles
            ORDER BY created_at DESC
        ''')
        return cursor.fetchall()

    def get_article(self, article_id: int) -> Optional[Dict[str, Any]]:
        """Get a complete article by ID"""
        # Get main article info
        cursor = self.conn.execute(
            'SELECT * FROM articles WHERE id = ?', (article_id,))
        article = cursor.fetchone()
        if not article:
            return None

        # Convert to dict and parse JSON fields
        result = dict(article)
        result['intro_paragraphs'] = json.loads(result['intro_paragraphs'])
        result['conclusion_paragraphs'] = json.loads(result['conclusion_paragraphs'])
        result['main_headings'] = []

        # Get main headings
        cursor = self.conn.execute(
            'SELECT * FROM main_headings WHERE article_id = ? ORDER BY position',
            (article_id,))
        for heading in cursor.fetchall():
            heading_dict = dict(heading)
            heading_dict['paragraphs'] = json.loads(heading_dict['paragraphs'])
            heading_dict['sub_headings'] = []

            # Get subheadings
            cursor2 = self.conn.execute(
                'SELECT * FROM sub_headings WHERE main_heading_id = ? ORDER BY position',
                (heading['id'],))
            for sub in cursor2.fetchall():
                sub_dict = dict(sub)
                sub_dict['paragraphs'] = json.loads(sub_dict['paragraphs'])
                sub_dict['sub_headings'] = []

                # Get sub-subheadings
                cursor3 = self.conn.execute(
                    'SELECT * FROM sub_sub_headings WHERE sub_heading_id = ? ORDER BY position',
                    (sub['id'],))
                for subsub in cursor3.fetchall():
                    subsub_dict = dict(subsub)
                    subsub_dict['paragraphs'] = json.loads(subsub_dict['paragraphs'])
                    sub_dict['sub_headings'].append(subsub_dict)

                heading_dict['sub_headings'].append(sub_dict)
            result['main_headings'].append(heading_dict)

        return result 