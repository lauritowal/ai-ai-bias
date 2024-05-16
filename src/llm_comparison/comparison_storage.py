# Collections are keyed by:
# * description_llm_engine,
# * description_prompt_key,
# * item_type
# * comparison_prompt_key
# * comparison_llm_engine
#
# The data is keyed by:
# * description_uid_1
# * description_uid_2
#
# The data is then just
# * winner (1, 2, or 0 for None/Invalid)

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
    -- Index
    comparison_prompt_key TEXT,
    comparison_llm_engine TEXT,
    description_uid_1 TEXT,
    description_uid_2 TEXT,
    
    -- Result: 0 for None/Invalid, 1 for description 1, 2 for description 2
    winner INTEGER,

    -- Additional info (for stats, cleaning the database, etc.)
    item_type TEXT,
    -- NB: these are only defined for LLM-Human comparisons, not between 2 LLMs
    description_llm_engine TEXT,
    description_prompt_key TEXT,
    -- Automatically added
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
    for schema in SQLITE_SCHEMA:
        conn.execute(schema)
    conn.commit()
    return conn


def db_stats(conn: sqlite3.Connection):
    cursor = conn.cursor()
    cursor.execute("SELECT COUNT(*) FROM comparison_results")
    total = cursor.fetchone()[0]
    cursor.execute("SELECT COUNT(*) FROM comparison_results WHERE winner = 0")
    invalid = cursor.fetchone()[0]
    s = f"Comparison DB statistics: total results: {total} total, {invalid} invalid"
    # Now we need to list all tuples (description_llm_engine, description_prompt_key, item_type, comparison_prompt_key, comparison_llm_engine) and count the rows of each
    cursor.execute(
        """SELECT description_llm_engine, description_prompt_key, item_type, comparison_prompt_key, comparison_llm_engine, COUNT(*)
        FROM comparison_results
        GROUP BY description_llm_engine, description_prompt_key, item_type, comparison_prompt_key, comparison_llm_engine
        ORDER BY comparison_llm_engine, comparison_prompt_key;
        """
    )
    s += "\n(comparison_llm_engine, comparison_prompt_key, description_llm_engine, description_prompt_key, item_type): counts"
    for row in cursor:
        cur2 = conn.cursor()
        # Count invalid results for this tuple
        cur2.execute(
            "SELECT COUNT(*) FROM comparison_results WHERE description_llm_engine = ? AND description_prompt_key = ? AND item_type = ? AND comparison_prompt_key = ? AND comparison_llm_engine = ? AND winner = 0",
            row[:5],
        )
        invalid = cur2.fetchone()[0]
        cur2.close()

        cur2 = conn.cursor()
        cur2.execute(
            "SELECT COUNT(*) FROM comparison_results WHERE winner = 1 AND description_llm_engine = ? AND description_prompt_key = ? AND item_type = ? AND comparison_prompt_key = ? AND comparison_llm_engine = ?",
            row[:5],
        )
        one = cur2.fetchone()[0]
        cur2.close()

        cur2 = conn.cursor()
        cur2.execute(
            "SELECT COUNT(*) FROM comparison_results WHERE winner = 2 AND description_llm_engine = ? AND description_prompt_key = ? AND item_type = ? AND comparison_prompt_key = ? AND comparison_llm_engine = ?",
            row[:5],
        )
        two = cur2.fetchone()[0]
        cur2.close()

        if one + two > 0:
            one_p = one / (row[5] - invalid)
            one_p_2 = one / (one + two)
            assert (one_p - one_p_2) < 0.01
        else:
            one_p = 0
        s += f"\n({row[4]}, {row[3]}, {row[2]}, {row[0]}, {row[1]}): {row[5]} total, {invalid} invalid, first option bias: {100 * one_p:.2f}%"
    cursor.close()
    return s


def db_get_comparison(
    conn: sqlite3.Connection,
    llm_engine: Engine,
    comparison_prompt_config: ComparisonPromptConfig,
    description_1: Description,
    description_2: Description,
) -> t.Optional[int]:
    """
    Returns 1 or 2 for the winner, 0 for invalid results (e.g. ties), and None if the comparison is not in the storage.
    """
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
    if row is None:
        return None
    return row[0]


def db_set_comparison(
    conn: sqlite3.Connection,
    llm_engine: Engine,
    comparison_prompt_config: ComparisonPromptConfig,
    description_1: Description,
    description_2: Description,
    winner: Description | None,
):
    assert (
        winner is None or winner == description_1 or winner == description_2
    ), f"Cached result must be None or one of the two descriptions being compared, got {winner} vs {description_1} vs {description_2}."
    winner_index = 0 if winner is None else (1 if winner == description_1 else 2)
    description_llm = (
        description_1 if description_1.origin == Origin.LLM else description_2
    )
    cursor = conn.cursor()
    cursor.execute(
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
            -- created_time is set by default
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
    cursor.connection.commit()
    cursor.close()
