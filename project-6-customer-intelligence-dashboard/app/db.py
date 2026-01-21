"""Database helpers for Supabase Postgres connections."""
from __future__ import annotations

import os

import pandas as pd
import streamlit as st
from dotenv import load_dotenv
from sqlalchemy import create_engine, text


@st.cache_resource
def get_engine():
    """Create a cached SQLAlchemy engine for Supabase."""
    load_dotenv()
    db_url = os.getenv("SUPABASE_DB_URL")
    if not db_url:
        raise ValueError("SUPABASE_DB_URL is not set. Add it to your .env file.")
    return create_engine(db_url, pool_pre_ping=True)


@st.cache_data(ttl=600)
def query_df(sql: str, params: dict | None = None) -> pd.DataFrame:
    """Run a SQL query and return a DataFrame."""
    engine = get_engine()
    with engine.connect() as connection:
        return pd.read_sql(text(sql), connection, params=params)
