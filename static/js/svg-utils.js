// Add this to your custom.js file or create a new file called svg-utils.js

// Utility function to create SVG elements with correct viewBox
function createSVGElement(width, height) {
    const svg = document.createElementNS("http://www.w3.org/2000/svg", "svg");
    svg.setAttribute("viewBox", `0 0 ${width} ${height}`);
    svg.setAttribute("width", "100%");
    svg.setAttribute("height", "100%");
    return svg;
}

// Example 1: Create a simple line SVG (e.g., for form field underlines)
function createLineSVG() {
    const svg = createSVGElement(100, 4);
    const line = document.createElementNS("http://www.w3.org/2000/svg", "line");
    line.setAttribute("x1", "0");
    line.setAttribute("y1", "2");
    line.setAttribute("x2", "100");
    line.setAttribute("y2", "2");
    line.setAttribute("stroke", "#000");
    line.setAttribute("stroke-width", "1");
    svg.appendChild(line);
    return svg;
}

// Example 2: Create a progress indicator SVG
function createProgressIndicator(progress) {
    const svg = createSVGElement(100, 100);
    const circle = document.createElementNS("http://www.w3.org/2000/svg", "circle");
    circle.setAttribute("cx", "50");
    circle.setAttribute("cy", "50");
    circle.setAttribute("r", "45");
    circle.setAttribute("fill", "none");
    circle.setAttribute("stroke", "#007bff");
    circle.setAttribute("stroke-width", "5");
    circle.setAttribute("stroke-dasharray", `${progress * 283} 283`);
    svg.appendChild(circle);
    return svg;
}

// Function to fix existing SVGs on the page
function fixExistingSVGs() {
    const svgs = document.querySelectorAll('svg[viewBox="0 0 100% 4"]');
    svgs.forEach(svg => {
        svg.setAttribute("viewBox", "0 0 100 4");
    });
}

// Initialize when the document is ready
document.addEventListener('DOMContentLoaded', () => {
    // Fix any existing SVGs
    fixExistingSVGs();
    
    // Example usage: Add a line SVG to an element
    const underlineElement = document.querySelector('.form-underline');
    if (underlineElement) {
        underlineElement.appendChild(createLineSVG());
    }
    
    // Example usage: Add a progress indicator
    const progressElement = document.querySelector('.progress-indicator');
    if (progressElement) {
        progressElement.appendChild(createProgressIndicator(0.75)); // 75% progress
    }
    
    // If you're dynamically creating SVGs after page load
    const observer = new MutationObserver(() => {
        fixExistingSVGs();
    });
    
    // Start observing the document for dynamically added SVGs
    observer.observe(document.body, {
        childList: true,
        subtree: true
    });
});