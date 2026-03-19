const { chromium } = require('playwright');
const fs = require('fs');
const path = require('path');

(async () => {
    let browser;
    try {
        browser = await chromium.connectOverCDP('http://localhost:9222');
        console.log('Connected to existing browser session.');
    } catch (e) {
        browser = await chromium.launch({ headless: false });
        console.log('Started new browser session.');
    }

    const context = browser.contexts()[0] || await browser.newContext();
    const page = (await context.pages())[0] || await context.newPage();

    try {
        console.log('Navigating to http://localhost:3000...');
        await page.goto('http://localhost:3000', { waitUntil: 'networkidle' });
        
        // Reload to apply hydration fixes
        await page.reload({ waitUntil: 'networkidle' });

        // Check if file is indexing
        const indexing = await page.locator('text=Analyzing...').count();
        if (indexing > 0) {
            console.log('Detected active indexing. Waiting...');
            await page.waitForSelector('text=What would you like to analyze?', { timeout: 300000 });
        } else {
            const detected = await page.locator('text=File Detected').count();
            if (detected === 0) {
                console.log('Uploading file...');
                await page.setInputFiles('input[type=\"file\"]', 'E:\\The_Council_v2\\backend\\uploads\\Liquor_Sales.csv');
                await page.waitForSelector('text=Arquivo recebido', { timeout: 10000 });
                console.log('Immediate feedback confirmed.');
                await page.waitForSelector('text=What would you like to analyze?', { timeout: 300000 });
            }
        }

        const queries = [
            'Quais os 3 produtos mais vendidos por categoria?',
            'Qual o vendor que obteve o maior faturamento total?',
            'Qual a média de valor de venda (Sale (Dollars)) por cidade? Liste as top 5.',
            'Existe alguma sazonalidade clara nas vendas? Analise por mês.',
            'Quais categorias tiveram a maior queda de vendas no período mais recente comparado ao anterior?'
        ];

        for (let i = 0; i < queries.length; i++) {
            console.log(`Executing Query ${i+1}: ${queries[i]}`);
            const chatInput = page.locator('input[placeholder=\"Ask The Council...\"]');
            await chatInput.fill(queries[i]);
            await chatInput.press('Enter');
            
            await page.waitForSelector('.animate-bounce', { state: 'detached', timeout: 300000 });
            await page.waitForTimeout(3000);

            const shotPath = `C:/Users/thiag/.gemini/antigravity/brain/a5a577be-4304-4925-a20f-06d750d759bb/ui_bench_q${i+1}.png`;
            await page.screenshot({ path: shotPath });
            console.log(`✅ Query ${i+1} completed. Screenshot: ${shotPath}`);
        }

        console.log('Requesting chart...');
        const chatInput = page.locator('input[placeholder=\"Ask The Council...\"]');
        await chatInput.fill('Gere um gráfico de barras com o top 10 produtos por volume de vendas.');
        await chatInput.press('Enter');
        await page.waitForSelector('.animate-bounce', { state: 'detached', timeout: 300000 });
        await page.waitForTimeout(5000);
        await page.screenshot({ path: 'C:/Users/thiag/.gemini/antigravity/brain/a5a577be-4304-4925-a20f-06d750d759bb/ui_bench_final_chart.png' });
        console.log('✅ Final chart rendered.');

    } catch (err) {
        console.error('Test Error:', err);
    } finally {
        // browser.close();
    }
})();
