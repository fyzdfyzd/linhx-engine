# Hanoi Events Database (TUNG TA TUNG TANG)

## Architecture Details
Implementing the LINHX LAB Scanning Pattern for events in Hanoi (March 2026).

### Configuration (`_CONFIG/`)
- **Event Schema**: standard `profile.md` for events involving Identity, Classification (5 dimensions), Event Details, Venue, Pricing, Description, and Source.
- **Event Taxonomy**: 
    - **Event Type (ET)**: 20 codes (ET01 Concert → ET20 Kids).
    - **Event Area (EA)**: 15 codes (EA01 Music → EA15 Business).
    - **Format (EF)**: Indoor, Outdoor, Hybrid, Online, Pop-up.
    - **Scale (ES)**: Intimate to Mega.
    - **Price Range (EP)**: Free to VIP.
- **Venue Registry**: 150+ identified venues including historical sites, theaters, creative spaces, and commercial centers.

### Scanning Strategy
The project evolved from using generated data to **real-time browser scanning** from verified hubs:
1. **Ticketbox.vn**: Primary source for concerts and ticketed shows.
2. **Hanoigrapevine.com**: Curated listings for art, photography, and cultural fusion.
3. **Web Search / Báo chí**: Traditional festivals, government-organized cultural programs, and trade shows.

## Cultural Heritage Insights
The database specifically catalogs the "Cultural Meaning" of Hanoi festivals, emphasizing the heritage economy:
- **Chùa Hương**: Pilgrimage, Buddhist traditions, and "going to the festival" culture.
- **Quan Họ (UNESCO)**: Art of social interaction and traditional singing in Kinh Bắc.
- **Thánh Gióng (UNESCO)**: Epic performance and patriotic symbols.
- **Thờ Mẫu (UNESCO)**: Mother Goddess religion and "Hầu Đồng" rituals.
- **Rối Nước (Water Puppetry)**: 1000-year-old tradition reflecting rice agriculture.

## Key Hubs Surveyed
- Ticketbox (Music/Concert)
- Hanoigrapevine (Art/Culture)
- Goethe-Institut, L'Espace, Japan Foundation (International Fusion)
- VNExpress, VOV, Sở VH-TT Hà Nội (Official Festivals)
- Vietbuild (Industrial/Trade)

## Lessons Learned & Best Practices
- **Real Data vs. Generated Data**: Initial attempts to generate event data for future dates (March 2026) resulted in high hallucination rates. The project pivoted to **browser-based scanning** and **web search verification** to ensure database integrity.
- **Workflow Orchestration**: Utilizing the **LinhX Crawl Server** (FastAPI at `http://localhost:8000/docs`) significantly increased scanning efficiency by allowing batch processing of HUB URLs with automatic fallback between HTTP and browser tiers.
- **Taxonomy Depth**: A 5-dimensional taxonomy is crucial for filtering large event datasets (Type, Area, Format, Scale, Price).
