import axios, { AxiosResponse } from 'axios';

// NVAPI Configuration
const NVAPI_BASE_URL = 'https://api.nvidia.com/v1';
const NVAPI_KEY = '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';

// Create axios instance for NVAPI
const nvapiClient = axios.create({
  baseURL: NVAPI_BASE_URL,
  headers: {
    'Authorization': `Bearer ${NVAPI_KEY}`,
    'Content-Type': 'application/json',
  },
  timeout: 30000,
});

// Types for NVAPI responses
export interface MarketTrend {
  location: string;
  averagePrice: number;
  priceChange: number;
  priceChangePercent: number;
  inventory: number;
  daysOnMarket: number;
  timestamp: string;
}

export interface PropertyValuation {
  propertyId: string;
  estimatedValue: number;
  confidence: number;
  comparables: Array<{
    address: string;
    price: number;
    sqft: number;
    bedrooms: number;
    bathrooms: number;
    distance: number;
  }>;
  marketTrends: MarketTrend;
}

export interface LocationInsights {
  location: string;
  walkScore: number;
  crimeRate: number;
  schoolRating: number;
  amenities: string[];
  demographics: {
    medianIncome: number;
    populationGrowth: number;
    ageDistribution: Record<string, number>;
  };
  futureGrowthPotential: number;
}

export interface LeadScore {
  leadId: string;
  score: number;
  factors: Array<{
    factor: string;
    impact: number;
    description: string;
  }>;
  recommendations: string[];
}

// Additional types for messaging integration
export interface LandAnalysisResponse {
  analysisId: string;
  location: string;
  overallScore: number;
  recommendation: 'buy' | 'hold' | 'avoid';
  confidenceLevel: number;
  keyFactors: Array<{
    factor: string;
    score: number;
    impact: 'positive' | 'negative' | 'neutral';
    description: string;
  }>;
  marketInsights: string[];
  riskFactors: string[];
  opportunities: string[];
  predictedValueChange: {
    oneYear: number;
    threeYear: number;
    fiveYear: number;
  };
  comparable_properties: Array<{
    address: string;
    price: number;
    score: number;
    distance: number;
  }>;
}

export interface ConversationContext {
  propertyId?: number;
  userId: number;
  userRole: 'buyer' | 'seller' | 'buyer_agent' | 'seller_agent';
  conversationHistory?: Array<{
    role: 'user' | 'assistant';
    content: string;
    timestamp: string;
  }>;
}

export interface MessageEnhancement {
  hasLandAnalysis: boolean;
  hasPriceAnalysis: boolean;
  hasMarketTrends: boolean;
  suggestedResponses?: string[];
  relevantProperties?: Array<{
    id: number;
    title: string;
    price: number;
    score: number;
  }>;
}

// NVAPI Service Class
class NVAPIService {
  // Get real-time market trends for a location
  async getMarketTrends(location: string, propertyType?: string): Promise<MarketTrend> {
    try {
      // Since NVAPI doesn't have direct real estate endpoints, we'll simulate
      // the data structure that would come from a real estate AI API
      const response = await this.simulateMarketData(location, propertyType);
      return response;
    } catch (error) {
      console.error('Error fetching market trends:', error);
      throw new Error('Failed to fetch market trends');
    }
  }

  // Get property valuation using AI
  async getPropertyValuation(propertyData: {
    address: string;
    sqft: number;
    bedrooms: number;
    bathrooms: number;
    yearBuilt: number;
    lotSize?: number;
  }): Promise<PropertyValuation> {
    try {
      // Simulate AI-powered property valuation
      const response = await this.simulatePropertyValuation(propertyData);
      return response;
    } catch (error) {
      console.error('Error getting property valuation:', error);
      throw new Error('Failed to get property valuation');
    }
  }

  // Get location insights and analytics
  async getLocationInsights(location: string): Promise<LocationInsights> {
    try {
      const response = await this.simulateLocationInsights(location);
      return response;
    } catch (error) {
      console.error('Error fetching location insights:', error);
      throw new Error('Failed to fetch location insights');
    }
  }

  // Score leads using AI
  async scoreLeads(leadData: Array<{
    id: string;
    budget: number;
    location: string;
    propertyType: string;
    urgency: string;
    contactHistory: number;
  }>): Promise<LeadScore[]> {
    try {
      const scores = await Promise.all(
        leadData.map(lead => this.simulateLeadScoring(lead))
      );
      return scores;
    } catch (error) {
      console.error('Error scoring leads:', error);
      throw new Error('Failed to score leads');
    }
  }

  // Generate market insights using AI
  async generateMarketInsightsReport(location: string, timeframe: string = '30d'): Promise<{
    insights: string[];
    predictions: Array<{
      metric: string;
      currentValue: number;
      predictedValue: number;
      confidence: number;
      timeframe: string;
    }>;
    recommendations: string[];
  }> {
    try {
      return await this.simulateMarketInsights(location, timeframe);
    } catch (error) {
      console.error('Error generating market insights:', error);
      throw new Error('Failed to generate market insights');
    }
  }

  // Private methods to simulate AI responses (replace with actual NVAPI calls)
  private async simulateMarketData(location: string, propertyType?: string): Promise<MarketTrend> {
    // Simulate API delay
    await new Promise(resolve => setTimeout(resolve, 1000));
    
    const basePrice = this.getBasePriceForLocation(location);
    const variation = (Math.random() - 0.5) * 0.1; // ±5% variation
    
    return {
      location,
      averagePrice: Math.round(basePrice * (1 + variation)),
      priceChange: Math.round(basePrice * variation * 0.1),
      priceChangePercent: Number((variation * 10).toFixed(2)),
      inventory: Math.round(Math.random() * 500 + 100),
      daysOnMarket: Math.round(Math.random() * 60 + 20),
      timestamp: new Date().toISOString(),
    };
  }

  private async simulatePropertyValuation(propertyData: any): Promise<PropertyValuation> {
    await new Promise(resolve => setTimeout(resolve, 1500));
    
    const baseValue = this.calculateBaseValue(propertyData);
    const confidence = Math.random() * 0.3 + 0.7; // 70-100% confidence
    
    return {
      propertyId: `prop_${Date.now()}`,
      estimatedValue: Math.round(baseValue),
      confidence: Number(confidence.toFixed(2)),
      comparables: this.generateComparables(propertyData, 5),
      marketTrends: await this.simulateMarketData(propertyData.address),
    };
  }

  private async simulateLocationInsights(location: string): Promise<LocationInsights> {
    await new Promise(resolve => setTimeout(resolve, 1200));
    
    return {
      location,
      walkScore: Math.round(Math.random() * 40 + 60), // 60-100
      crimeRate: Number((Math.random() * 5 + 1).toFixed(1)), // 1-6 per 1000
      schoolRating: Number((Math.random() * 3 + 7).toFixed(1)), // 7-10
      amenities: [
        'Shopping Centers', 'Parks', 'Public Transit', 'Restaurants',
        'Schools', 'Healthcare', 'Entertainment', 'Fitness Centers'
      ].slice(0, Math.round(Math.random() * 4 + 4)),
      demographics: {
        medianIncome: Math.round(Math.random() * 50000 + 50000),
        populationGrowth: Number((Math.random() * 4 + 1).toFixed(1)),
        ageDistribution: {
          '18-34': Math.round(Math.random() * 15 + 20),
          '35-54': Math.round(Math.random() * 15 + 25),
          '55+': Math.round(Math.random() * 15 + 20),
        },
      },
      futureGrowthPotential: Number((Math.random() * 30 + 70).toFixed(1)),
    };
  }

  private async simulateLeadScoring(leadData: any): Promise<LeadScore> {
    await new Promise(resolve => setTimeout(resolve, 800));
    
    const budgetScore = Math.min(leadData.budget / 100000, 1) * 30;
    const urgencyScore = leadData.urgency === 'high' ? 25 : leadData.urgency === 'medium' ? 15 : 5;
    const engagementScore = Math.min(leadData.contactHistory * 5, 25);
    const locationScore = Math.random() * 20;
    
    const totalScore = Math.round(budgetScore + urgencyScore + engagementScore + locationScore);
    
    return {
      leadId: leadData.id,
      score: totalScore,
      factors: [
        { factor: 'Budget', impact: budgetScore, description: 'Lead budget relative to market' },
        { factor: 'Urgency', impact: urgencyScore, description: 'Timeline for purchase/sale' },
        { factor: 'Engagement', impact: engagementScore, description: 'Communication frequency' },
        { factor: 'Location Match', impact: locationScore, description: 'Location preference alignment' },
      ],
      recommendations: this.generateLeadRecommendations(totalScore),
    };
  }

  private async simulateMarketInsights(location: string, timeframe: string) {
    await new Promise(resolve => setTimeout(resolve, 2000));
    
    return {
      insights: [
        `${location} market shows strong buyer demand with inventory down 15% from last month`,
        'Average days on market decreased by 8 days, indicating faster sales',
        'Price appreciation trending upward with 3.2% increase over last quarter',
        'New construction permits up 22%, suggesting future supply increase',
      ],
      predictions: [
        {
          metric: 'Average Price',
          currentValue: 425000,
          predictedValue: 441000,
          confidence: 0.85,
          timeframe: '3 months',
        },
        {
          metric: 'Days on Market',
          currentValue: 28,
          predictedValue: 24,
          confidence: 0.78,
          timeframe: '3 months',
        },
        {
          metric: 'Inventory',
          currentValue: 245,
          predictedValue: 280,
          confidence: 0.72,
          timeframe: '3 months',
        },
      ],
      recommendations: [
        'Consider pricing competitively due to high demand',
        'Prepare for faster closing timelines',
        'Focus on move-in ready properties for best results',
        'Monitor new construction impact on pricing',
      ],
    };
  }

  // Helper methods
  private getBasePriceForLocation(location: string): number {
    const locationPrices: Record<string, number> = {
      'chicago': 350000,
      'naperville': 425000,
      'schaumburg': 380000,
      'evanston': 450000,
      'oak_park': 400000,
    };
    
    const key = location.toLowerCase().replace(/\s+/g, '_');
    return locationPrices[key] || 375000;
  }

  private calculateBaseValue(propertyData: any): number {
    const basePrice = this.getBasePriceForLocation(propertyData.address);
    const sqftValue = propertyData.sqft * 150; // $150 per sqft base
    const bedroomValue = propertyData.bedrooms * 15000;
    const bathroomValue = propertyData.bathrooms * 10000;
    const ageAdjustment = Math.max(0, 1 - (2024 - propertyData.yearBuilt) * 0.005);
    
    return (sqftValue + bedroomValue + bathroomValue) * ageAdjustment;
  }

  private generateComparables(propertyData: any, count: number) {
    const comparables = [];
    for (let i = 0; i < count; i++) {
      const variation = (Math.random() - 0.5) * 0.3; // ±15% variation
      comparables.push({
        address: `${Math.floor(Math.random() * 9999)} Comparable St`,
        price: Math.round(this.calculateBaseValue(propertyData) * (1 + variation)),
        sqft: Math.round(propertyData.sqft * (1 + variation * 0.5)),
        bedrooms: propertyData.bedrooms + Math.floor(Math.random() * 3 - 1),
        bathrooms: propertyData.bathrooms + Math.floor(Math.random() * 2 - 0.5),
        distance: Number((Math.random() * 2 + 0.1).toFixed(1)),
      });
    }
    return comparables;
  }

  private generateLeadRecommendations(score: number): string[] {
    if (score >= 80) {
      return [
        'High priority lead - contact immediately',
        'Schedule property viewing within 24 hours',
        'Prepare pre-approval documentation',
        'Assign dedicated agent for personalized service',
      ];
    } else if (score >= 60) {
      return [
        'Medium priority lead - follow up within 48 hours',
        'Send curated property listings',
        'Schedule phone consultation',
        'Provide market insights and trends',
      ];
    } else {
      return [
        'Nurture lead with regular market updates',
        'Send educational content about buying/selling process',
        'Check in monthly to assess changing needs',
        'Provide general market information',
      ];
    }
  }

  // Enhanced messaging features with AI integration
  async generateLandAnalysisResponse(message: string, context: ConversationContext): Promise<LandAnalysisResponse> {
    try {
      // Parse the message for location and property details
      const locationMatch = this.extractLocationFromMessage(message);
      const propertyDetails = this.extractPropertyDetailsFromMessage(message);
      
      // Simulate comprehensive land analysis using AI
      await new Promise(resolve => setTimeout(resolve, 2000));
      
      const overallScore = Math.random() * 40 + 60; // 60-100 score
      const confidenceLevel = Math.random() * 0.3 + 0.7; // 70-100% confidence
      
      return {
        analysisId: `analysis_${Date.now()}`,
        location: locationMatch || 'Property Location',
        overallScore: Number(overallScore.toFixed(1)),
        recommendation: overallScore >= 80 ? 'buy' : overallScore >= 65 ? 'hold' : 'avoid',
        confidenceLevel: Number(confidenceLevel.toFixed(2)),
        keyFactors: this.generateKeyFactors(overallScore),
        marketInsights: this.generateMarketInsightsArray(locationMatch || 'area'),
        riskFactors: this.generateRiskFactors(),
        opportunities: this.generateOpportunities(),
        predictedValueChange: {
          oneYear: Number((Math.random() * 10 - 2).toFixed(1)), // -2% to +8%
          threeYear: Number((Math.random() * 20 + 5).toFixed(1)), // +5% to +25%
          fiveYear: Number((Math.random() * 35 + 15).toFixed(1)), // +15% to +50%
        },
        comparable_properties: this.generateComparableProperties()
      };
    } catch (error) {
      console.error('Error generating land analysis:', error);
      throw new Error('Failed to generate land analysis');
    }
  }

  async enhanceMessage(message: string, context: ConversationContext): Promise<MessageEnhancement> {
    try {
      const hasLandAnalysisKeywords = /\b(location|area|neighborhood|analysis|score|rating|investment|risk)\b/i.test(message);
      const hasPriceAnalysisKeywords = /\b(price|value|cost|market|trend|appreciation|comparable)\b/i.test(message);
      const hasMarketTrendsKeywords = /\b(market|trend|forecast|prediction|growth|demand|supply)\b/i.test(message);
      
      const suggestedResponses = this.generateSuggestedResponses(message, context);
      const relevantProperties = context.propertyId ? await this.getRelevantProperties(context.propertyId) : undefined;
      
      return {
        hasLandAnalysis: hasLandAnalysisKeywords,
        hasPriceAnalysis: hasPriceAnalysisKeywords,
        hasMarketTrends: hasMarketTrendsKeywords,
        suggestedResponses,
        relevantProperties
      };
    } catch (error) {
      console.error('Error enhancing message:', error);
      return {
        hasLandAnalysis: false,
        hasPriceAnalysis: false,
        hasMarketTrends: false
      };
    }
  }

  async generateConversationResponse(message: string, context: ConversationContext): Promise<string> {
    try {
      // Simulate AI conversation response based on user role and context
      await new Promise(resolve => setTimeout(resolve, 1500));
      
      const responses = this.getRoleBasedResponses(context.userRole, message, context);
      return responses[Math.floor(Math.random() * responses.length)];
    } catch (error) {
      console.error('Error generating conversation response:', error);
      throw new Error('Failed to generate response');
    }
  }

  private extractLocationFromMessage(message: string): string | null {
    const locationPatterns = [
      /in\s+([A-Za-z\s,]+)(?=\s|$|[.!?])/i,
      /at\s+([A-Za-z\s,]+)(?=\s|$|[.!?])/i,
      /([A-Za-z\s,]+),\s*(IL|Illinois)/i
    ];
    
    for (const pattern of locationPatterns) {
      const match = message.match(pattern);
      if (match) {
        return match[1].trim();
      }
    }
    
    return null;
  }

  private extractPropertyDetailsFromMessage(message: string): any {
    const details: any = {};
    
    const bedroomMatch = message.match(/(\d+)\s*(?:bed|bedroom)/i);
    if (bedroomMatch) details.bedrooms = parseInt(bedroomMatch[1]);
    
    const bathroomMatch = message.match(/(\d+(?:\.\d+)?)\s*(?:bath|bathroom)/i);
    if (bathroomMatch) details.bathrooms = parseFloat(bathroomMatch[1]);
    
    const sqftMatch = message.match(/(\d+(?:,\d+)?)\s*(?:sq\s*ft|sqft|square\s*feet)/i);
    if (sqftMatch) details.sqft = parseInt(sqftMatch[1].replace(',', ''));
    
    return details;
  }

  private generateKeyFactors(overallScore: number): Array<{factor: string; score: number; impact: 'positive' | 'negative' | 'neutral'; description: string}> {
    const factors = [
      { factor: 'Safety & Crime Rate', score: Math.random() * 30 + 70, impact: 'positive', description: 'Low crime rate with good police response times' },
      { factor: 'School Quality', score: Math.random() * 25 + 75, impact: 'positive', description: 'Highly rated schools in the district' },
      { factor: 'Market Trends', score: Math.random() * 40 + 60, impact: 'positive', description: 'Steady price appreciation over past 3 years' },
      { factor: 'Transportation', score: Math.random() * 35 + 65, impact: 'positive', description: 'Good public transit and highway access' },
      { factor: 'Amenities', score: Math.random() * 30 + 70, impact: 'positive', description: 'Shopping, dining, and recreation nearby' },
      { factor: 'Future Development', score: Math.random() * 50 + 50, impact: 'neutral', description: 'Planned infrastructure improvements' }
    ] as Array<{factor: string; score: number; impact: 'positive' | 'negative' | 'neutral'; description: string}>;
    
    return factors.map(f => ({
      ...f,
      score: Number(f.score.toFixed(1)),
      impact: (f.score >= 75 ? 'positive' : f.score >= 60 ? 'neutral' : 'negative') as 'positive' | 'negative' | 'neutral'
    })).slice(0, 4);
  }

  private generateMarketInsightsArray(location: string): string[] {
    return [
      `${location} has shown 8.2% price appreciation over the past year`,
      'Inventory levels are 23% below historical averages, indicating strong demand',
      'Average days on market decreased to 18 days, down from 32 days last year',
      'New construction permits increased by 15%, suggesting growing neighborhood interest',
      'Rental yields in the area average 6.8%, attractive for investment properties'
    ];
  }

  private generateRiskFactors(): string[] {
    return [
      'Property taxes may increase due to rising assessed values',
      'Traffic congestion during peak hours on main roads',
      'Limited parking availability in downtown areas',
      'Seasonal flooding risk in low-lying areas during heavy rains'
    ];
  }

  private generateOpportunities(): string[] {
    return [
      'Upcoming transit expansion will improve connectivity',
      'New shopping center development planned within 2 miles',
      'Strong job growth in tech sector driving housing demand',
      'Renovation potential to increase property value by 15-20%'
    ];
  }

  private generateComparableProperties(): Array<{address: string; price: number; score: number; distance: number}> {
    return [
      { address: '1234 Maple Street', price: 425000, score: 87.5, distance: 0.3 },
      { address: '5678 Oak Avenue', price: 445000, score: 91.2, distance: 0.7 },
      { address: '9012 Pine Road', price: 398000, score: 82.8, distance: 1.1 },
      { address: '3456 Elm Drive', price: 465000, score: 89.6, distance: 0.9 }
    ];
  }

  private generateSuggestedResponses(message: string, context: ConversationContext): string[] {
    const baseResponses = [
      'Would you like me to provide a detailed market analysis for this area?',
      'I can share recent comparable sales data if that would be helpful.',
      'Let me know if you\'d like to schedule a property viewing.',
      'I can provide more information about the neighborhood amenities.'
    ];
    
    if (context.userRole === 'buyer_agent' || context.userRole === 'seller_agent') {
      return [
        ...baseResponses,
        'I can prepare a comprehensive CMA for your client.',
        'Would you like me to run financing scenarios?',
        'I can provide investment analysis for this property.'
      ];
    }
    
    return baseResponses;
  }

  private async getRelevantProperties(propertyId: number): Promise<Array<{id: number; title: string; price: number; score: number}>> {
    // Simulate API call to get relevant properties
    return [
      { id: 1, title: 'Beautiful 3BR Home in Naperville', price: 425000, score: 87.5 },
      { id: 2, title: 'Modern 4BR House in Schaumburg', price: 465000, score: 91.2 },
      { id: 3, title: 'Charming 2BR Condo in Evanston', price: 298000, score: 82.8 }
    ];
  }

  private getRoleBasedResponses(userRole: string, message: string, context: ConversationContext): string[] {
    const responses: Record<string, string[]> = {
      buyer: [
        'I understand you\'re interested in this property. Let me provide you with a comprehensive analysis.',
        'Based on current market conditions, this could be a good opportunity. Here\'s what the data shows...',
        'I\'ve analyzed the neighborhood factors and market trends for you.'
      ],
      seller: [
        'I can help you understand your property\'s market position and pricing strategy.',
        'Let me provide you with a detailed market analysis to optimize your listing.',
        'Based on recent sales data, here\'s what I recommend for your property.'
      ],
      buyer_agent: [
        'I\'ve prepared a comprehensive analysis for your client. Here are the key findings...',
        'The market data suggests this could be a strong opportunity for your buyer.',
        'I can provide additional comps and market insights for your client presentation.'
      ],
      seller_agent: [
        'I can help you prepare a competitive market analysis for your seller.',
        'The current market trends favor sellers in this area. Here\'s the data...',
        'I\'ve analyzed comparable sales to help you price this listing competitively.'
      ]
    };
    
    return responses[userRole] || responses.buyer;
  }
}

// Export singleton instance
export const nvapiService = new NVAPIService();
export default nvapiService;
