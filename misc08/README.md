# Bologna Rider

|         |                                |
| ------- | ------------------------------ |
| Authors | Karina Chichifoi <@TryKatChup> |
| Points  | 500                            |
| Tags    | misc,osint                     |

## Challenge Description

Trve riders, recognize this spot?

_Flag format:_ `UlisseCTF{name_of_the_place}`

### Description

Participants were given an image of a road sign covered with numerous motorcycle-themed stickers, indicating directions towards `Bologna 45` and partially revealing `Monghidoro` underneath the stickers. The presence of many biker stickers clearly hints at a popular destination for motorcyclists.

The challenge purpose was to identify the location where the photo was taken.

![biker jpg](writeup/biker.jpg)

### 🔍 Solution

- Searching online with keywords such as `"monghidoro motorcycle destination"`, the first result page displays:

  - [Komoot - Road Cycling Routes around Monghidoro](https://www.komoot.com/guide/582867/road-cycling-routes-around-monghidoro)
  - [Motorcycle Diaries - Raticosa-Futa-Muraglione](https://motorcycle-diaries.com/it/roads/raticosa-futa-muraglione-and-back)

- Using Google Maps, participants verify which suggested destination is approximately 45 km from Bologna.

  - **Passo della Raticosa** emerges as the exact match.

- Confirming through Google Street View, the same heavily stickered sign is clearly visible at an intersection at Passo della Raticosa, reinforcing the identification.

![street view](writeup/maps_street_view.png)

- The flag format was:
  ```
  UlisseCTF{name_of_the_location}
  ```

indicating that the solution isn't merely the name of a road but a specific named location.
