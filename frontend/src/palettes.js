export const PALETTES = {
    purples: ['#4361ee', '#3a0ca3', '#7209b7', '#560bad', '#480ca8', '#3f37c9', '#4895ef', '#4cc9f0', '#3a86ff', '#0096c7'],
    rainbow: ['#ff006e', '#8338ec', '#3a86ff', '#00f5d4', '#fb5607', '#ff006e', '#3a86ff', '#ffbe0b', '#06d6a0', '#118ab2'],
    nature: ['#2d6a4f', '#40916c', '#52b788', '#74c69d', '#95d5b2', '#1b4332', '#081c15', '#1b4332', '#2d6a4f', '#40916c'],
    ocean: ['#03045e', '#0077b6', '#00b4d8', '#90e0ef', '#023e8a', '#0096c7', '#48cae4', '#ade8f4', '#caf0f8', '#014f86'],
    sunset: ['#ff6b6b', '#f06595', '#cc5de8', '#845ef7', '#5c7cfa', '#339af0', '#22b8cf', '#20c997', '#51cf66', '#94d82d']
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