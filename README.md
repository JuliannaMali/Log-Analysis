LogAnalyzer:

    Cel projektu:

        Celem projektu LogAnalyzer jest stworzenie systemu do analizowania logów w sposób rozproszony i skalowalny. Projekt umożliwia:

        Wrzucanie logów ręcznie lub generowanie przykładowych logów.

        Przetwarzanie logów przez wiele workerów w tle

        Monitorowanie statusu tasku

        Analizę najczęściej występujących słów w logach.

        Filtrowanie logów po poziomie lub słowie kluczowym oraz wyliczanie procentowego udziału.

        Eksport przetworzonych logów do pliku CSV.

        Projekt rozwiązuje problem analizy dużych ilości logów w systemach produkcyjnych, umożliwiając ich szybką obróbkę i wizualizację wyników w interfejsie webowym.
    
    Uruchomienie projektu:

        Wymaga przynajmniej wersji Docker 20.0 (na komputerze autora v28.1.1)
        Wymaga przynajmniej Docker Compose 2.0 (na komputerze autora v2.35.1)

    Budowanie usługi:

            docker-compose up --build --scale worker=3 (liczba workerów jest skalowalna, 3 jest przykładową cyfrą)

        Aby dostać się do usługi należy w przeglądarce wejść na http://localhost:8000/

        Po zakończeniu korzystania należy użyć komendy docker-compose down

    Korzystanie z systemu:
        Wgrywanie logów:
            Do pola tekstowego należy wpisać log w formie {POZIOM} {tekst}, np ERROR password incorrect.
            Poziom zawsze musi być z dużych liter
            Jest 5 poziomów: ["INFO", "ERROR", "WARNING", "DEBUG", "CRITICAL"]

        Logi można wygenerować za pomocą przycisku generuj logi - zostanie wygenerowane 5000 przykładowych logów

        Sprawdzanie statusu:
            Task ID powinno pojawić się automatycznie - można na bieżąco sprawdzać ile logów zostało już przerobionych, aktualną liczbę poszczególnych poziomów, jakie słowa się powtarzają najczęściej, który worker przerobił ile

        Filtorwanie:
            Można przefiltrować po poziomie (należy wpisać z dużych liter), po pojedynczym słowie kluczowym lub po obu. Pokażą się wszystkie logi pasujące do filtrów, ile ich jest oraz jaki stanowią procent wszystkich

        Eksport CSV:
            Zwłaszcza przy uzyciu funkcji Generuj logi, można je potem wszystkie pobrać w formacie CSV

    Działanie systemu
        Każdy task dzieli logi na chunk’i po 30 linii.
        Chunk’i trafiają do Redis queue, skąd pobierają je workery.
        Workery przetwarzają logi i aktualizują:
            licznik przetworzonych chunków,
            liczbę logów wg poziomu,
            słowa i ich częstotliwość,
            który worker przetworzył ile logów.
        Po zakończeniu wszystkich chunków task oznaczany jest jako done.