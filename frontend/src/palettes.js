export const PALETTES = {
    purples: ['#4361ee', '#3a0ca3', '#7209b7', '#560bad', '#480ca8', '#3f37c9', '#4895ef', '#4cc9f0', '#3a86ff', '#0096c7'],
    rainbow: ['#ff006e', '#8338ec', '#3a86ff', '#00f5d4', '#fb5607', '#ff006e', '#3a86ff', '#ffbe0b', '#06d6a0', '#118ab2'],
    nature: ['#2d6a4f', '#40916c', '#52b788', '#74c69d', '#95d5b2', '#1b4332', '#081c15', '#1b4332', '#2d6a4f', '#40916c'],
    ocean: ['#03045e', '#0077b6', '#00b4d8', '#90e0ef', '#023e8a', '#0096c7', '#48cae4', '#ade8f4', '#caf0f8', '#014f86'],
    sunset: ['#ff6b6b', '#f06595', '#cc5de8', '#845ef7', '#5c7cfa', '#339af0', '#22b8cf', '#20c997', '#51cf66', '#94d82d'],
    blushMorning: ['#f8c8dc', '#f4a7b9', '#e58f96', '#d7a6c0', '#c5b6e3', '#b7d4ea', '#a7e4d4', '#b9ebad', '#dde295', '#fce7ab'],
    softGreensBlues: ['#c6e0b4', '#9fdfd8', '#8fc0c2', '#92b4d4', '#9abded', '#adc8e6', '#bccfe6', '#d4d9e3', '#e8e3e5', '#f2f1f0'],
    gentleSunset: ['#ffb4a2', '#ffcdb2', '#ffe5d9', '#fae1dd', '#f8edeb', '#d8e2dc', '#b7d8d6', '#a1c9c9', '#9eb8b3', '#a1aab7'],
    moodyTwilight: ['#1b1d36', '#2c2f48', '#4b536e', '#68788b', '#8ea4bd', '#a6c4d3', '#91d8d8', '#69aab7', '#3f687e', '#2c485c'],
    mutedNocturne: ['#343a40', '#495057', '#868e96', '#adb5bd', '#dee2e6', '#212529', '#40494f', '#3b5a68', '#486f7d', '#548a9e'],
    coolNightGlow: ['#2e3440', '#3b4252', '#434c5e', '#4c566a', '#d8dee9', '#e5e9f0', '#eceff4', '#88c0d0', '#81a1c1', '#5e81ac']
};


export class PaletteManager {
    constructor(paletteName = 'purples') {
        this.setPalette(paletteName);
    }

    setPalette(name) {
        if (!(name in PALETTES)) {
            throw new Error(`Unknown palette: ${name}`);
        }
        this.currentPalette = PALETTES[name];
    }

    getColor(index) {
        return this.currentPalette[index % this.currentPalette.length];
    }
}