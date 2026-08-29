import tempfile
from pathlib import Path
from game.questions import QuestionManager, QuestionPair


def test_question_manager_loads_assets():
    # Test loading actual assets directory
    assets_path = Path(__file__).parent.parent / "assets"
    manager = QuestionManager(assets_dir=assets_path)
    manager.load_all()

    assert len(manager.categories) >= 2
    assert "hobbies" in [c.lower() for c in manager.categories] or any(
        "hobbies" in c.lower() for c in manager.categories
    )

    pair = manager.get_random_pair(used_ids=set())
    assert pair is not None
    assert isinstance(pair, QuestionPair)
    assert pair.main_question != ""
    assert pair.spy_question != ""
    assert pair.main_question != pair.spy_question
    assert pair.id != ""


def test_question_manager_non_recurrence():
    with tempfile.TemporaryDirectory() as tmp_dir:
        tmp_path = Path(tmp_dir)
        csv_file = tmp_path / "test_theme.csv"
        csv_file.write_text(
            "id,питання\n1,Питання 1\n2,Питання 2\n3,Питання 3\n4,Питання 4\n",
            encoding="utf-8",
        )

        manager = QuestionManager(assets_dir=tmp_path)
        manager.load_all()

        used_ids = set()
        pair1 = manager.get_random_pair(used_ids=used_ids)
        assert pair1 is not None
        used_ids.add(pair1.id)

        pair2 = manager.get_random_pair(used_ids=used_ids)
        assert pair2 is not None
        assert pair2.id not in used_ids
        used_ids.add(pair2.id)

        # When all pairs are exhausted, it should either raise or recycle with a flag
        # In our implementation, if used_ids contains all, it can recycle gracefully
        pair3 = manager.get_random_pair(used_ids=used_ids)
        assert pair3 is not None


def test_question_manager_paired_csv():
    with tempfile.TemporaryDirectory() as tmp_dir:
        tmp_path = Path(tmp_dir)
        csv_file = tmp_path / "paired.csv"
        csv_file.write_text(
            "main_question,spy_question\n"
            "Яка твоя улюблена страва?,Який твій улюблений напій?\n"
            "Де ти мрієш жити?,Куди ти хочеш у відпустку?\n",
            encoding="utf-8",
        )

        manager = QuestionManager(assets_dir=tmp_path)
        manager.load_all()

        used_ids = set()
        pair1 = manager.get_random_pair(used_ids=used_ids)
        assert pair1 is not None
        assert pair1.main_question in ["Яка твоя улюблена страва?", "Де ти мрієш жити?"]
        if pair1.main_question == "Яка твоя улюблена страва?":
            assert pair1.spy_question == "Який твій улюблений напій?"
