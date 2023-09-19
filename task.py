class Task():
    """
    Třída pro vytváření instancí úkolů.
    """
    def __init__(self, date, subject, details):
        self.date = date
        self.subject = subject
        self.details = details

    def __str__(self):
        return f'Datum úkolu: {date}\nNázev úkolu:  {subject}\nPodrobnosti:  {details}'
