export const PALETTES = {
    Purples: ['#4361ee', '#3a0ca3', '#7209b7', '#560bad', '#480ca8', '#3f37c9', '#4895ef', '#4cc9f0', '#3a86ff', '#0096c7'],
    Nature: ['#2d6a4f', '#40916c', '#52b788', '#74c69d', '#95d5b2', '#1b4332', '#081c15', '#1b4332', '#2d6a4f', '#40916c'],
    Ocean: ['#03045e', '#0077b6', '#00b4d8', '#90e0ef', '#023e8a', '#0096c7', '#48cae4', '#ade8f4', '#caf0f8', '#014f86'],
    Sunset: ['#ff6b6b', '#f06595', '#cc5de8', '#845ef7', '#5c7cfa', '#339af0', '#22b8cf', '#20c997', '#51cf66', '#94d82d'],
    DaisyDIsk: ['#affc62', '#5894f8', '#eb51a4', '#7943f5', '#7c3b8a', '#fcd34d', '#34d399', '#60a5fa', '#c084fc', '#f87171']

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