import { test, expect } from '@playwright/test';
import path from 'path';

test.describe('Fluxo de Análise The Council 2.0', () => {
  test('deve fazer upload de um CSV e renderizar um gráfico de análise', async ({ page }) => {
    // 1. Navegar para a aplicação
    await page.goto('/');
    await expect(page).toHaveTitle(/The Council/);

    // 2. Preparar o ficheiro de teste (usando o test_chart.csv do backend)
    const filePath = path.resolve(__dirname, '../../backend/test_chart.csv');
    
    // 3. Realizar o Upload
    const fileChooserPromise = page.waitForEvent('filechooser');
    // The button has the 'Upload' text based on current implementation
    await page.click('button:has-text("Upload")'); 
    const fileChooser = await fileChooserPromise;
    await fileChooser.setFiles(filePath);

    // 4. Verificar se o upload foi bem-sucedido na UI
    // The assistant responds with "**File Detected**" and "indexed this datasource"
    await expect(page.locator('text=indexed this datasource')).toBeVisible({ timeout: 10000 });

    // 5. Enviar comando de análise no Chat
    const chatInput = page.locator('textarea[placeholder*="Ask the Council"]');
    await chatInput.fill('Analyze this data and show me a trend chart');
    await page.keyboard.press('Enter');

    // 6. Validar a "Semantic Orchestra" (Logs e Spans em execução)
    // The system shows the agent name in the tag
    await expect(page.locator('text=analyst')).toBeVisible({ timeout: 15000 });

    // 7. Validação Final: Renderização do Gráfico Plotly
    // The component ChartRenderer generates a container with class .js-plotly-plot
    const plotlyChart = page.locator('.js-plotly-plot');
    await expect(plotlyChart).toBeVisible({ timeout: 20000 });

    // 8. Verificar se o SVG do gráfico foi realmente desenhado
    const chartSvg = plotlyChart.locator('svg.main-svg');
    await expect(chartSvg).toBeVisible();
  });
});
