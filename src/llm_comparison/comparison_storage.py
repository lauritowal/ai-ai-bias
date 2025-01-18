import functools
import logging
import os
import sqlite3
import typing as t
from pathlib import Path

from llm_comparison.config import ComparisonPromptConfig
from llm_comparison.llm_comparison import Description
from llm_descriptions_generator.schema import Engine, Origin

SQLITE_SCHEMA = [
    """
CREATE TABLE IF NOT EXISTS comparison_results (
    comparison_prompt_key TEXT,
    comparison_llm_engine TEXT,
    description_uid_1 TEXT,
    description_uid_2 TEXT,
    winner INTEGER,
    item_type TEXT,
    description_llm_engine TEXT,
    description_prompt_key TEXT,
    created_time TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    created_user TEXT,
    created_host TEXT,
    UNIQUE(description_uid_1, description_uid_2, comparison_llm_engine, comparison_prompt_key)
);""",
    """
CREATE UNIQUE INDEX IF NOT EXISTS comparison_results_index ON comparison_results (
    description_uid_1, description_uid_2, comparison_llm_engine, comparison_prompt_key
);
""",
]

def get_comparison_results_db(path: Path) -> sqlite3.Connection:
    logging.info(f"Opening comparison results database at {path}")
    conn = sqlite3.connect(path, check_same_thread=False)
    with conn:
        for schema in SQLITE_SCHEMA:
            conn.execute(schema)
    return conn

def db_stats(conn: sqlite3.Connection):
    cursor = conn.cursor()
    cursor.execute("SELECT COUNT(*) FROM comparison_results")
    total = cursor.fetchone()[0]
    cursor.execute("SELECT COUNT(*) FROM comparison_results WHERE winner = 0")
    invalid = cursor.fetchone()[0]
    s = f"Comparison DB statistics: total results: {total} total, {invalid} invalid"

    cursor.execute(
        """SELECT description_llm_engine, description_prompt_key, item_type, comparison_prompt_key, comparison_llm_engine, COUNT(*)
        FROM comparison_results
        GROUP BY description_llm_engine, description_prompt_key, item_type, comparison_prompt_key, comparison_llm_engine
        ORDER BY comparison_llm_engine, comparison_prompt_key;"""
    )
    s += "\n(comparison_llm_engine, comparison_prompt_key, description_llm_engine, description_prompt_key, item_type): counts"
    
    for row in cursor:
        cursor.execute(
            "SELECT COUNT(*) FROM comparison_results WHERE description_llm_engine = ? AND description_prompt_key = ? AND item_type = ? AND comparison_prompt_key = ? AND comparison_llm_engine = ? AND winner = 0",
            row[:5],
        )
        invalid_count = cursor.fetchone()[0]
        cursor.execute(
            "SELECT COUNT(*) FROM comparison_results WHERE winner = 1 AND description_llm_engine = ? AND description_prompt_key = ? AND item_type = ? AND comparison_prompt_key = ? AND comparison_llm_engine = ?",
            row[:5],
        )
        one = cursor.fetchone()[0]
        cursor.execute(
            "SELECT COUNT(*) FROM comparison_results WHERE winner = 2 AND description_llm_engine = ? AND description_prompt_key = ? AND item_type = ? AND comparison_prompt_key = ? AND comparison_llm_engine = ?",
            row[:5],
        )
        two = cursor.fetchone()[0]

        if one + two > 0:
            assert one + two + invalid_count == row[5]
            one_p = one / (one + two)
        else:
            one_p = 0
        s += f"\n({row[4]}, {row[3]}, {row[2]}, {row[0]}, {row[1]}): {row[5]} total, {invalid_count} invalid, first option bias: {100 * one_p:.2f}%"

    cursor.execute(
        """SELECT comparison_llm_engine, COUNT(*)
        FROM comparison_results
        GROUP BY comparison_llm_engine
        ORDER BY comparison_llm_engine;"""
    )
    
    for row in cursor:
        cursor.execute(
            "SELECT COUNT(*) FROM comparison_results WHERE winner = 0 AND comparison_llm_engine = ?",
            row[:1],
        )
        invalid = cursor.fetchone()[0]
        cursor.execute(
            "SELECT COUNT(*) FROM comparison_results WHERE winner = 1 AND comparison_llm_engine = ?",
            row[:1],
        )
        one = cursor.fetchone()[0]
        cursor.execute(
            "SELECT COUNT(*) FROM comparison_results WHERE winner = 2 AND comparison_llm_engine = ?",
            row[:1],
        )
        two = cursor.fetchone()[0]

        if one + two > 0:
            assert one + two + invalid == row[1]
            one_p = one / (one + two)
        else:
            one_p = 0
        s += f"\n({row[0]}: {row[1]} total, {invalid} invalid, first option bias: {100 * one_p:.2f}%"
    
    cursor.close()
    return s

def db_get_comparison(
    conn: sqlite3.Connection,
    llm_engine: Engine,
    comparison_prompt_config: ComparisonPromptConfig,
    description_1: Description,
    description_2: Description,
) -> t.Optional[int]:
    cursor = conn.cursor()
    cursor.execute(
        """
        SELECT winner
        FROM comparison_results
        WHERE description_uid_1 = ?
          AND description_uid_2 = ?
          AND comparison_llm_engine = ?
          AND comparison_prompt_key = ?
        """,
        (
            description_1.uid,
            description_2.uid,
            llm_engine,
            comparison_prompt_config.prompt_key,
        ),
    )
    row = cursor.fetchone()
    cursor.close()
    return None if row is None else row[0]

def db_set_comparison(
    conn: sqlite3.Connection,
    llm_engine: Engine,
    comparison_prompt_config: ComparisonPromptConfig,
    description_1: Description,
    description_2: Description,
    winner: Description | None,
):
    assert (
        winner is None or winner.uid == description_1.uid or winner.uid == description_2.uid
    ), f"Cached result must be None or one of the two descriptions being compared, got {winner} vs {description_1} vs {description_2}."
    
    winner_index = 0 if winner is None else (1 if winner == description_1 else 2)
    description_llm = (
        description_1 if description_1.origin == Origin.LLM else description_2
    )
    
    with conn:
        conn.execute(
            """
            INSERT OR REPLACE INTO comparison_results (
                comparison_prompt_key,
                comparison_llm_engine,
                description_uid_1,
                description_uid_2,
                winner,
                item_type,
                description_llm_engine,
                description_prompt_key,
                created_user,
                created_host
                ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?);
            """,
            (
                comparison_prompt_config.prompt_key,
                llm_engine.value,
                description_1.uid,
                description_2.uid,
                winner_index,
                comparison_prompt_config.item_type,
                description_llm.engine.value,
                description_llm.prompt_key,
                os.getlogin(),
                os.uname().nodename,
            ),
        )