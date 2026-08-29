import csv
import logging
import random
from pathlib import Path
from game.models import QuestionPair

logger = logging.getLogger(__name__)


class QuestionManager:
    def __init__(self, assets_dir: Path | str = "assets"):
        self.assets_dir = Path(assets_dir)
        self.categories: dict[str, list[QuestionPair]] = {}
        self.all_pairs: list[QuestionPair] = []

    def load_all(self) -> None:
        """Scan assets directory and load all CSV question files."""
        self.categories.clear()
        self.all_pairs.clear()

        if not self.assets_dir.exists():
            logger.warning(f"Assets directory {self.assets_dir} does not exist.")
            return

        csv_files = sorted(self.assets_dir.glob("*.csv"))
        if not csv_files:
            logger.warning(f"No CSV files found in {self.assets_dir}.")
            return

        for file_path in csv_files:
            self._load_file(file_path)

        logger.info(
            f"Loaded {len(self.all_pairs)} question pairs from {len(self.categories)} categories."
        )

    def _load_file(self, file_path: Path) -> None:
        category_name = (
            file_path.stem.replace("spy_questions_", "").replace("_", " ").title()
        )
        pairs: list[QuestionPair] = []

        try:
            with open(file_path, mode="r", encoding="utf-8", errors="replace") as f:
                reader = csv.reader(f)
                rows = [
                    row for row in reader if row and any(cell.strip() for cell in row)
                ]

            if not rows:
                return

            header = [cell.strip().lower() for cell in rows[0]]
            data_rows = rows[1:]

            # Case 1: Explicit pair columns (e.g., main_question, spy_question)
            if "main_question" in header and "spy_question" in header:
                main_idx = header.index("main_question")
                spy_idx = header.index("spy_question")
                for idx, row in enumerate(data_rows):
                    if len(row) > max(main_idx, spy_idx):
                        main_q = row[main_idx].strip()
                        spy_q = row[spy_idx].strip()
                        if main_q and spy_q:
                            pair_id = f"{file_path.stem}:{idx}"
                            pairs.append(
                                QuestionPair(
                                    id=pair_id,
                                    main_question=main_q,
                                    spy_question=spy_q,
                                    category=category_name,
                                )
                            )

            # Case 2: Single question per row (e.g. id,питання or question)
            else:
                questions = []
                q_idx = 1 if len(header) > 1 and "id" in header[0] else 0
                for row in data_rows:
                    if len(row) > q_idx:
                        q_text = row[q_idx].strip()
                        if q_text:
                            questions.append(q_text)

                if len(questions) >= 2:
                    # Create pairs from consecutive/shuffled items in the same theme
                    for i in range(len(questions)):
                        # Pair question i with question i+1 (or wrap around)
                        next_i = (i + 1) % len(questions)
                        main_q = questions[i]
                        spy_q = questions[next_i]
                        pair_id = f"{file_path.stem}:{i}_{next_i}"
                        pairs.append(
                            QuestionPair(
                                id=pair_id,
                                main_question=main_q,
                                spy_question=spy_q,
                                category=category_name,
                            )
                        )

            if pairs:
                self.categories[category_name] = pairs
                self.all_pairs.extend(pairs)

        except Exception as e:
            logger.error(f"Error loading questions from {file_path}: {e}")

    def get_random_pair(
        self, used_ids: set[str] | None = None, category: str | None = None
    ) -> QuestionPair:
        """
        Get an unused question pair.
        If all question pairs have been used in the session, falls back to the full pool.
        """
        if not self.all_pairs:
            self.load_all()

        if not self.all_pairs:
            # Fallback default pair if no CSV assets exist
            return QuestionPair(
                id="default:0",
                main_question="Яке твоє улюблене хобі?",
                spy_question="Чим ти займаєшся у вільний час?",
                category="General",
            )

        used_ids = used_ids or set()
        pool = (
            self.categories.get(category, self.all_pairs)
            if category
            else self.all_pairs
        )

        available = [p for p in pool if p.id not in used_ids]
        if not available:
            # All questions used in this session; recycle pool
            available = pool

        return random.choice(available)
