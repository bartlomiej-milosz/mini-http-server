# Sockety — notatka

## Czym jest socket

Socket to **interfejs między twoim kodem a kernelem** który faktycznie ogarnia sieć.
Ty wywołujesz metody na sockecie → socket tłumaczy to na rozkazy kernela → kernel wysyła dane przez sieć.

```
Twój kod (Python)
      │
      │  socket API  (bind, listen, accept, recv, send)
      │
      ▼
    Kernel          ← tu dzieje się prawdziwa robota
      │
      ▼
    Sieć
```

Sam socket nic nie przechowuje — to tylko uchwyt (file descriptor, zwykła liczba całkowita).
Cały stan połączenia, bufory, kolejki — trzyma kernel.

---

## Tworzenie socketu

```python
socket.socket(address_family, socket_type)
```

### 1. Address Family — format adresu

| Stała | Format | Przykład użycia |
|-------|--------|-----------------|
| `AF_INET` | IPv4 | `192.168.1.1:8080` — 99% internetu |
| `AF_INET6` | IPv6 | `2001:db8::1` — nowoczesna infrastruktura |
| `AF_UNIX` | ścieżka pliku | `/var/run/app.sock` — komunikacja między procesami na tym samym komputerze |

### 2. Socket Type — sposób transmisji

| Stała | Protokół | Charakterystyka |
|-------|----------|-----------------|
| `SOCK_STREAM` | TCP | ciągły strumień bajtów, kernel gwarantuje kolejność i dostarczenie |
| `SOCK_DGRAM` | UDP | osobne niezależne paczki (datagramy), brak gwarancji, szybciej |
| `SOCK_RAW` | surowy | ręczne nagłówki IP, wymaga roota, używany przez ping/nmap |

---

## TCP vs UDP

```
TCP — strumień:
  wysyłasz → [H][e][l][l][o][ ][W][o][r][l][d]
             ciągły strumień, kernel skleja i gwarantuje kolejność
  używany przez: HTTP, SSH, FTP

UDP — datagramy:
  wysyłasz → [paczka 1] [paczka 2] [paczka 3]
             osobne paczki, mogą dotrzeć w złej kolejności lub wcale
  używany przez: DNS, gry online, streaming, VoIP
```

---

## Ważne opcje socketu

```python
# Zawsze dodawaj przy serwerach TCP — pozwala od razu rebindować port po restarcie
# Bez tego: "Address already in use" przez ~60s (stan TIME_WAIT)
server_socket.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
#                        poziom: ogólny  opcja: reużyj adres    włącz
```

---

## Typowy flow serwera TCP

```python
# 1. Stwórz socket
server_socket = socket.socket(AF_INET, SOCK_STREAM)

# 2. Skonfiguruj
server_socket.setsockopt(SOL_SOCKET, SO_REUSEADDR, 1)

# 3. Zarezerwuj adres i port w kernelu
server_socket.bind(("127.0.0.1", 8080))

# 4. Zacznij nasłuchiwać (BACKLOG = kolejka oczekujących połączeń)
server_socket.listen(5)

# 5. Czekaj na połączenia
client_socket, address = server_socket.accept()  # blokuje wątek

# 6. Odbieraj i wysyłaj bajty
data: bytes = client_socket.recv(1024)
client_socket.sendall(b"odpowiedz")
```

---

## Przez socket płyną bajty, nie tekst

```python
# Sieć nie zna pojęcia "tekst" — przesyła surowe bajty (liczby 0-255)

data = client_socket.recv(1024)
print(type(data))   # <class 'bytes'>

# bytes → str
text = data.decode("utf-8")

# str → bytes (przed wysłaniem)
client_socket.sendall(text.encode("utf-8"))
```

---

## Socket ≠ protokół

Socket to interfejs **do używania** protokołów. TCP i UDP to protokoły — zasady jak dane mają być przesyłane.
Socket to uchwyt przez który z tych protokołów korzystasz.
