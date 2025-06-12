# Program Stegano

Program służy do ukrywania i wyodrębniania wiadomości w plikach HTML przy użyciu różnych metod steganograficznych.

## Pliki wejściowe/wyjściowe

- `mess.txt` - plik z wiadomością do ukrycia (ciąg bitów w formacie szesnastkowym, gdzie każdy znak `[0-9,a-e]` reprezentuje 4 bity)
- `cover.html` - oryginalny plik HTML służący jako nośnik (musi być znacznie większy niż wiadomość)
- `watermark.html` - wynikowy plik HTML z ukrytą wiadomością (tworzony przy opcji `-e`)
- `detect.txt` - plik z wyodrębnioną wiadomością (tworzony przy opcji `-d`)

## Sposób użycia

Program przyjmuje następujące opcje:
./stegano [opcja] [metoda]

text

Gdzie:
- `-e` - tryb zanurzania wiadomości (embed)
- `-d` - tryb wyodrębniania wiadomości (detect)
- `-1`, `-2`, `-3`, `-4` - wybór metody ukrywania wiadomości

## Metody ukrywania wiadomości

### Metoda 1 (`-1`)
- Każdy bit wiadomości jest kodowany jako dodatkowa spacja na końcu wiersza
- Maksymalna długość wiadomości: liczba wierszy w nośniku

### Metoda 2 (`-2`)
- Każdy bit jest kodowany jako pojedyncza (0) lub podwójna spacja (1)
- Tabulatory pozostają bez zmian
- Maksymalna długość wiadomości: liczba pojedynczych spacji w nośniku

### Metoda 3 (`-3`)
- Bity są kodowane jako celowe błędy w nazwach atrybutów:
  - `0` → błąd w `margin-bottom` (np. "margin-botom")
  - `1` → błąd w `line-height` (np. "lineheight")
- Atrybuty są dodawane do znaczników `<p>` bez określonej wysokości/marginesu

### Metoda 4 (`-4`)
- Bity są kodowane jako nadmiarowe znaczniki:
  - `1` → `<font></font><font>` (otwarcie-zamknięcie-otwarcie)
  - `0` → `</font></font>` (podwójne zamknięcie)
- Maksymalna długość wiadomości: liczba znaczników `<font>` w nośniku

## Uwagi

1. Przed ukryciem wiadomości program usuwa wszystkie przypadkowe sekwencje, które mogłyby zakłócić proces:
   - spacje na końcach wierszy
   - podwójne spacje
   - nieprawidłowe nazwy atrybutów
   - nadmiarowe pary znaczników

2. W trybie `-e` program zwraca błąd, jeśli nośnik jest za mały do przekazania całej wiadomości.

3. Wiadomość w pliku `mess.txt` jest traktowana jako ciąg bitów w zapisie szesnastkowym (podobnie jak wyniki funkcji skrótu).