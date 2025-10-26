import os
from typing import List

import praw
from langchain.schema import Document
from langchain_core.callbacks import CallbackManagerForRetrieverRun
from langchain_core.retrievers import BaseRetriever
from typing_extensions import Self, override


class RedditClient:
    def __init__(self, user_agent: str):
        self.reddit_client = praw.Reddit(
            client_id=os.getenv("REDDIT_APP_ID"),
            client_secret=os.getenv("REDDIT_APP_SECRET"),
            user_agent=user_agent,
        )
        self.reddit_search_client = self.reddit_client.subreddit("godot").search

    def as_retriever(self, k: int, relevance: str) -> "RedditRetriever":
        """
        Return self as a retriever.
        sort (str): Select one of "relevance", "hot", "top", "new", or "comments"
        """
        return RedditRetriever(
            reddit_client=self,
            k=k,
            relevance=relevance,
        )

    def search_with_query(
        self, query: str, sort: str = "relevance", limit: int = 10
    ) -> List[Document]:
        """Search for posts relevant to query.

        Args:
            query (str): The search query.
            sort (str): Select one of "relevance", "hot", "top", "new", or "comments"

        Returns:
            List[Documents]: _description_
        """
        all_posts = []
        posts = self.reddit_search_client(
            query,
            sort=sort,
            time_filter="all",
            limit=limit,
        )

        for post in posts:
            title = f"# {post.title}\n"
            content = post.selftext
            comments = "\n".join(
                [
                    f"**Comment {i+1}:**\n{comment.body}"
                    for i, comment in enumerate(post.comments)
                ]
            )
            metadata = {
                "author": post.author.name,
                "score": post.score,
                "upvote_ratio": post.upvote_ratio,
                "num_comments": post.num_comments,
            }
            all_posts.append(
                Document(page_content=title + content + comments, metadata=metadata)
            )

        return all_posts


class RedditRetriever(BaseRetriever):
    k: int
    """Number of top results to return"""
    reddit_client: RedditClient
    """Reddit client to use for searching."""
    relevance: str
    """Relevance of the search results."""

    @override
    def _get_relevant_documents(
        self, query: str, *, run_manager: CallbackManagerForRetrieverRun = None
    ) -> List[Document]:
        """Sync implementations for retriever."""
        documents = self.reddit_client.search_with_query(
            query=query,
            sort=self.relevance,
            limit=self.k,
        )

        return documents
