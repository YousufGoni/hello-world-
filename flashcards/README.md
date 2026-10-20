# Flash Cards

A tiny study app in a single file: `index.html`. No installs, no server.

## Use it

Double-click `index.html` to open it in your browser (or drag it into a browser window).

1. **Make a deck**: type a name and click *Add deck*.
2. **Add cards**: fill in the front (question) and back (answer).
3. **Study**: click *Study*, then click the card (or press **Space**) to flip it.
   Use **← / →** or the buttons to move between cards. Turn on *Shuffle* to mix them up.

**Starter decks**: under *Starter decks*, click *Add* next to **Periodic table** to get
118 ready-made cards (symbol on the front; name, atomic number and family on the back).

## How it works

- **HTML** describes the three screens (deck list, deck editor, study mode).
- **CSS** (in `<style>`) handles the look, dark mode, and the 3D flip.
  The flip works like a real index card: the answer is printed on the back,
  and rotating the card 180° turns it over.
- **JavaScript** (in `<script>`) keeps all your decks in one object called `data`,
  and a `render()` function redraws the page from it after every change.

Your cards are saved in the browser's **localStorage**: a little notebook the
browser keeps for this page. It stays on *this* browser on *this* computer, so
if you open the file on another device or clear your browsing data, you'll
start with an empty set.
