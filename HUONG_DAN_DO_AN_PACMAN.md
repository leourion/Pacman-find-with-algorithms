# Huong dan do an Pacman AI

Tai lieu nay dung de giai thich nhanh cach chay, cach demo va y nghia cac che do AI dang duoc dung trong game Pacman.

## 1. Muc tieu do an

Do an mo phong game Pacman bang Pygame, trong do Pacman co the duoc dieu khien thu cong hoac tu dong tim duong den muc tieu bang cac thuat toan tim kiem.

Phan quan trong cua do an la truc quan hoa qua trinh tim duong:

- Duong di du kien cua Pacman.
- Cac node ma thuat toan da xet.
- Thu tu pop node trong hang doi/stack/priority queue.
- So sanh so buoc, chi phi, so node da tham va thoi gian chay giua cac thuat toan.

## 2. Cach chay chuong trinh

Chay truc tiep:

```bash
python main.py
```

Neu dung `uv`:

```bash
uv run main.py
```

## 3. Cac phim dieu khien chinh

| Phim | Chuc nang |
| --- | --- |
| Mui ten | Dieu khien Pacman o che do Manual |
| 1 | Manual Control |
| 2 | BFS |
| 3 | DFS |
| 4 | UCS |
| 5 | A* |
| 6 | GBFS |
| G | Tao goal moi khi dang o che do AI |
| H | Doi heuristic Manhattan/Euclidean cho A* va GBFS |
| V | Bat/tat hien thi visited nodes |
| P | Bat/tat hien thi path mau xanh |
| L | Bat/tat duong noi giua cac visited nodes |
| A | Doi giua visited hien tai va visited tich luy |
| I | Bat/tat bang trace chi tiet |
| S | Bat/tat step mode |
| SPACE | Di tiep 1 buoc trong step mode |
| TAB | Bat/tat bang so sanh thuat toan |
| E | Xuat ket qua so sanh ra CSV |
| F | Bat/tat che do an ghost |
| R | Reset game |

## 4. Cac che do AI dang dung

### Manual Control

Pacman do nguoi choi dieu khien bang phim mui ten. Che do nay dung de choi thu cong hoac kiem tra map.

### BFS - Breadth-First Search

BFS mo rong cac node theo tung lop, tu gan den xa.

Dac diem:

- Tim duong co so buoc ngan nhat neu moi buoc co cung cost.
- Thuong tham nhieu node vi phai quet rong.
- Phu hop de demo y tuong "tim theo chieu rong".

### DFS - Depth-First Search

DFS di sau vao mot nhanh truoc, sau do moi quay lai cac nhanh khac.

Dac diem:

- Co the tim ra duong nhanh trong mot so map.
- Khong dam bao duong ngan nhat.
- De thay su khac biet voi BFS vi thu tu visited thuong tap trung theo mot nhanh sau.

### UCS - Uniform Cost Search

UCS chon node co tong cost tu start den node do nho nhat.

Trong game nay, moi loai o co cost khac nhau:

| Loai o | Cost |
| --- | ---: |
| DOT | 1 |
| POWER | 1 |
| EMPTY | 2 |
| Vung ghost-house | +5 |

Dac diem:

- Tim duong co tong chi phi thap nhat.
- Khong chi quan tam so buoc, ma quan tam di qua o nao.
- Vi phai dam bao toi uu theo cost, UCS co the xet nhieu nhanh khong nam tren duong di cuoi cung.

### A* Search

A* dung cong thuc:

```text
f(n) = g(n) + h(n)
```

Trong do:

- `g(n)`: cost tu start den node `n`.
- `h(n)`: uoc luong khoang cach tu node `n` den goal.
- `f(n)`: diem uu tien de chon node tiep theo.

Dac diem:

- Ket hop cost thuc te va du doan khoang cach con lai.
- Thuong tham it node hon UCS.
- Co the doi heuristic bang phim `H`.

### GBFS - Greedy Best-First Search

GBFS dung cong thuc:

```text
f(n) = h(n)
```

GBFS chi nhin vao uoc luong khoang cach den goal, khong quan tam cost da di.

Dac diem:

- Thuong chay nhanh va lao ve phia goal.
- Khong dam bao duong toi uu.
- De demo su khac nhau giua "nhin gan goal" va "tim duong re/ngan nhat".

## 5. Y nghia cac hinh anh truc quan

### Duong xanh la

Duong xanh la la path hien tai ma Pacman se di theo.

Path nay la ket qua sau khi thuat toan da tim xong duong tu vi tri Pacman den goal.

### Cham xanh duong

Cham xanh duong la cac visited nodes, tuc la nhung o thuat toan da tham hoac da xet trong qua trinh tim duong.

Neu so visited lon, thuat toan da phai kham pha nhieu o hon.

### Visited tich luy

Khi bat che do accumulated visited, man hinh hien tat ca node da duoc tham qua nhieu lan replan, khong chi lan tim duong moi nhat.

Che do nay giup thay tong khu vuc ma AI da kham pha trong ca qua trinh choi.

## 6. Bang trace khi bam I

Bang `I` hien chi tiet qua trinh tim duong cua UCS, A* va GBFS.

Vi du:

```text
#   node       parent     edge   g      h      f
183 (15,26)   (15,25)    2      24     0.0    24.0
184 (6,22)    (7,22)     1      25     0.0    25.0
190 (5,22)    (6,22)     1      26     0.0    26.0
```

Y nghia tung cot:

| Cot | Y nghia |
| --- | --- |
| `#` | Thu tu node duoc lay ra de xet |
| `node` | O hien tai dang duoc xet, dang `(row, col)` |
| `parent` | O truoc do dan toi `node` trong duong tot nhat hien tai |
| `edge` | Cost de di vao node do |
| `g` | Tong cost tu start den node |
| `h` | Heuristic, uoc luong khoang cach tu node den goal |
| `f` | Gia tri uu tien cua thuat toan |

Luu y quan trong:

- Hai dong lien tiep trong bang khong nhat thiet la hai o lien tiep tren duong di.
- Cot `#` chi cho biet thu tu thuat toan pop node ra de xet.
- Quan he duong di phai doc bang cap `parent -> node`.

Vi du:

```text
183 (15,26) parent (15,25)
184 (6,22)  parent (7,22)
```

Dong 183 va 184 duoc xet lien tiep, nhung khong phai cha-con cua nhau.

Quan he dung la:

```text
(15,25) -> (15,26)
(7,22)  -> (6,22)
```

Thuat toan van xet cac node khong nam tren duong cuoi cung vi no can so sanh nhieu kha nang truoc khi ket luan duong nao la tot nhat.

## 7. Step mode

Step mode dung de demo Pacman di tung buoc theo path.

Cach dung:

1. Chon mot che do AI bang phim `2`, `3`, `4`, `5` hoac `6`.
2. Bam `S` de bat step mode.
3. Bam `SPACE` de Pacman di tiep mot buoc.

Che do nay giup nguoi xem thay ro Pacman khong di ngau nhien, ma di theo path da duoc thuat toan tinh truoc.

## 8. Bang so sanh khi bam TAB

Bang so sanh dung de xem hieu nang cac thuat toan sau moi lan tim duong.

Nhung chi so can quan tam:

| Chi so | Y nghia |
| --- | --- |
| steps | So buoc trong path |
| visited | So node thuat toan da tham |
| cost | Tong chi phi duong di |
| time_ms | Thoi gian tim duong |

Cach demo:

1. Chon UCS bang phim `4`, quan sat cost va visited.
2. Chon A* bang phim `5`, so sanh visited va time.
3. Chon GBFS bang phim `6`, quan sat toc do va chat luong path.
4. Bam `TAB` de hien bang so sanh.
5. Bam `E` de xuat file CSV neu can dua vao bao cao.

## 9. Goi y noi khi thuyet trinh

Co the trinh bay theo thu tu:

1. Game Pacman duoc dung lam moi truong truc quan cho bai toan tim duong tren luoi.
2. Moi o tren map la mot node, moi lan di sang o ke ben la mot edge.
3. BFS va DFS minh hoa hai chien luoc tim kiem co ban.
4. UCS them trong so cho moi o nen tim duong theo cost nho nhat.
5. A* them heuristic de huong viec tim kiem ve goal, giam so node can xet.
6. GBFS chi dung heuristic nen nhanh nhung khong dam bao toi uu.
7. Bang `I` cho thay noi bo thuat toan: node nao duoc xet, parent cua no la ai, va vi sao node do duoc uu tien.
8. Bang `TAB` cho phep so sanh bang so lieu thay vi chi nhin bang mat.

## 10. Ket luan ngan

Do an the hien duoc su khac nhau giua cac thuat toan tim kiem tren cung mot moi truong game:

- BFS toi uu theo so buoc neu cost bang nhau.
- DFS tim theo chieu sau nhung khong dam bao toi uu.
- UCS toi uu theo tong cost.
- A* can bang giua cost da di va uoc luong den goal.
- GBFS nhanh vi chi bam theo goal, nhung co the khong toi uu.

Phan truc quan hoa giup nguoi xem khong chi thay Pacman di den dich, ma con thay duoc thuat toan da suy nghi va loai tru cac kha nang nhu the nao.
