from app.models import Transaction


class Action:
    def __init__(self, category: str | None = None, tags: list[str] | None = None):
        self.category = category
        self.tags = tags

    def apply(self, transaction: Transaction):
        if self.category:
            transaction.category = self.category

        if self.tags:
            if transaction.tags is None:
                transaction.tags = []
            for tag in self.tags:
                if tag not in transaction.tags:
                    transaction.tags.append(tag)
