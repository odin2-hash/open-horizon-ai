import React, { useState, useEffect } from 'react';
import { Card } from '../components/ui/Card';
import { Button } from '../components/ui/Button';
import { Input } from '../components/ui/Input';
import { Badge } from '../components/ui/Badge';
import { Users, Search, MapPin, Building, Mail, Globe, Star, Plus, Filter } from 'lucide-react';

interface Partner {
  id: string;
  name: string;
  country: string;
  organization_type: string;
  expertise_areas: string[];
  erasmus_code: string;
  contact_email: string;
  contact_website: string;
  contact_phone?: string;
  compatibility_score: number;
  partnership_rationale: string;
  verified: boolean;
  metadata: any;
}

interface SearchCriteria {
  query: string;
  countries: string[];
  expertise_areas: string[];
  organization_types: string[];
}

export const PartnersPage: React.FC = () => {
  const [partners, setPartners] = useState<Partner[]>([]);
  const [filteredPartners, setFilteredPartners] = useState<Partner[]>([]);
  const [searchCriteria, setSearchCriteria] = useState<SearchCriteria>({
    query: '',
    countries: [],
    expertise_areas: [],
    organization_types: []
  });
  const [selectedPartner, setSelectedPartner] = useState<Partner | null>(null);
  const [isSearching, setIsSearching] = useState(false);

  // Sample partner data
  const samplePartners: Partner[] = [
    {
      id: '1',
      name: 'Digital Youth Foundation',
      country: 'Germany',
      organization_type: 'NGO',
      expertise_areas: ['Digital Skills', 'Youth Work', 'Innovation'],
      erasmus_code: 'DE-YOUTH-001',
      contact_email: 'contact@digitalyouth.de',
      contact_website: 'https://digitalyouth.de',
      compatibility_score: 9,
      partnership_rationale: 'Strong digital expertise and proven track record in youth projects',
      verified: true,
      metadata: {}
    },
    {
      id: '2',
      name: 'Green Action Network',
      country: 'Netherlands',
      organization_type: 'NGO',
      expertise_areas: ['Environmental Education', 'Sustainability', 'Community Engagement'],
      erasmus_code: 'NL-GREEN-002',
      contact_email: 'info@greenaction.nl',
      contact_website: 'https://greenaction.nl',
      compatibility_score: 8,
      partnership_rationale: 'Excellent environmental focus with European-wide networks',
      verified: true,
      metadata: {}
    },
    {
      id: '3',
      name: 'Inclusion Works',
      country: 'Spain',
      organization_type: 'Public Body',
      expertise_areas: ['Social Inclusion', 'Diversity Training', 'Youth Support'],
      erasmus_code: 'ES-INCL-003',
      contact_email: 'hello@inclusionworks.es',
      contact_website: 'https://inclusionworks.es',
      compatibility_score: 7,
      partnership_rationale: 'Specialized in inclusion work with vulnerable groups',
      verified: true,
      metadata: {}
    },
    {
      id: '4',
      name: 'Innovation Academy',
      country: 'Finland',
      organization_type: 'Higher Education Institution',
      expertise_areas: ['Innovation', 'Entrepreneurship', 'Technology'],
      erasmus_code: 'FI-INNOV-004',
      contact_email: 'partnerships@innovacademy.fi',
      contact_website: 'https://innovacademy.fi',
      compatibility_score: 8,
      partnership_rationale: 'Academic excellence in innovation and strong research capabilities',
      verified: true,
      metadata: {}
    },
    {
      id: '5',
      name: 'Youth Bridge Europe',
      country: 'France',
      organization_type: 'NGO',
      expertise_areas: ['Cultural Exchange', 'Language Learning', 'European Citizenship'],
      erasmus_code: 'FR-BRIDGE-005',
      contact_email: 'europe@youthbridge.fr',
      contact_website: 'https://youthbridge.fr',
      compatibility_score: 7,
      partnership_rationale: 'Extensive experience in cross-cultural youth programs',
      verified: true,
      metadata: {}
    }
  ];

  useEffect(() => {
    // Load partners from localStorage or use sample data
    const saved = localStorage.getItem('partner_database');
    if (saved) {
      setPartners(JSON.parse(saved));
    } else {
      setPartners(samplePartners);
      localStorage.setItem('partner_database', JSON.stringify(samplePartners));
    }
  }, []);

  useEffect(() => {
    // Filter partners based on search criteria
    let filtered = partners;

    if (searchCriteria.query) {
      const query = searchCriteria.query.toLowerCase();
      filtered = filtered.filter(partner => 
        partner.name.toLowerCase().includes(query) ||
        partner.expertise_areas.some(area => area.toLowerCase().includes(query)) ||
        partner.partnership_rationale.toLowerCase().includes(query)
      );
    }

    if (searchCriteria.countries.length > 0) {
      filtered = filtered.filter(partner => 
        searchCriteria.countries.includes(partner.country)
      );
    }

    if (searchCriteria.expertise_areas.length > 0) {
      filtered = filtered.filter(partner =>
        searchCriteria.expertise_areas.some(area =>
          partner.expertise_areas.includes(area)
        )
      );
    }

    if (searchCriteria.organization_types.length > 0) {
      filtered = filtered.filter(partner =>
        searchCriteria.organization_types.includes(partner.organization_type)
      );
    }

    // Sort by compatibility score
    filtered.sort((a, b) => b.compatibility_score - a.compatibility_score);

    setFilteredPartners(filtered);
  }, [partners, searchCriteria]);

  const searchPartners = async () => {
    setIsSearching(true);
    // Simulate AI-powered partner search
    setTimeout(() => {
      setIsSearching(false);
    }, 2000);
  };

  const getScoreColor = (score: number) => {
    if (score >= 8) return 'text-green-600 dark:text-green-400';
    if (score >= 6) return 'text-yellow-600 dark:text-yellow-400';
    return 'text-red-600 dark:text-red-400';
  };

  const getTypeColor = (type: string) => {
    switch (type) {
      case 'NGO': return 'bg-blue-100 text-blue-800 dark:bg-blue-900 dark:text-blue-300';
      case 'Higher Education Institution': return 'bg-purple-100 text-purple-800 dark:bg-purple-900 dark:text-purple-300';
      case 'Public Body': return 'bg-green-100 text-green-800 dark:bg-green-900 dark:text-green-300';
      case 'Company': return 'bg-orange-100 text-orange-800 dark:bg-orange-900 dark:text-orange-300';
      default: return 'bg-gray-100 text-gray-800 dark:bg-gray-900 dark:text-gray-300';
    }
  };

  const countries = Array.from(new Set(partners.map(p => p.country))).sort();
  const allExpertiseAreas = Array.from(new Set(partners.flatMap(p => p.expertise_areas))).sort();
  const organizationTypes = Array.from(new Set(partners.map(p => p.organization_type))).sort();

  return (
    <div className="space-y-6">
      <div className="text-center space-y-4">
        <div className="flex items-center justify-center gap-3">
          <Users className="h-8 w-8 text-blue-500" />
          <h1 className="text-4xl font-bold bg-gradient-to-r from-blue-600 to-green-600 dark:from-blue-400 dark:to-green-400 bg-clip-text text-transparent">
            Partner Discovery
          </h1>
        </div>
        <p className="text-lg text-gray-600 dark:text-gray-400 max-w-2xl mx-auto">
          Find the perfect European partners for your Erasmus+ project. Search by expertise, 
          location, and organization type.
        </p>
      </div>

      {/* Search and Filters */}
      <Card className="p-6">
        <div className="space-y-4">
          <div className="flex gap-4">
            <div className="flex-1">
              <Input
                placeholder="Search partners, expertise areas, or keywords..."
                value={searchCriteria.query}
                onChange={(e) => setSearchCriteria({ ...searchCriteria, query: e.target.value })}
                className="text-lg"
              />
            </div>
            <Button onClick={searchPartners} disabled={isSearching} className="px-6">
              <Search className="h-4 w-4 mr-2" />
              {isSearching ? 'Searching...' : 'Search'}
            </Button>
          </div>

          {/* Advanced Filters */}
          <div className="grid grid-cols-1 md:grid-cols-3 gap-4">
            <div>
              <label className="block text-sm font-medium mb-2">Countries</label>
              <select
                multiple
                className="w-full p-2 border border-gray-300 dark:border-gray-600 rounded-lg bg-white dark:bg-gray-800 max-h-32 overflow-y-auto"
                value={searchCriteria.countries}
                onChange={(e) => {
                  const values = Array.from(e.target.selectedOptions, option => option.value);
                  setSearchCriteria({ ...searchCriteria, countries: values });
                }}
              >
                {countries.map(country => (
                  <option key={country} value={country}>{country}</option>
                ))}
              </select>
            </div>

            <div>
              <label className="block text-sm font-medium mb-2">Expertise Areas</label>
              <select
                multiple
                className="w-full p-2 border border-gray-300 dark:border-gray-600 rounded-lg bg-white dark:bg-gray-800 max-h-32 overflow-y-auto"
                value={searchCriteria.expertise_areas}
                onChange={(e) => {
                  const values = Array.from(e.target.selectedOptions, option => option.value);
                  setSearchCriteria({ ...searchCriteria, expertise_areas: values });
                }}
              >
                {allExpertiseAreas.map(area => (
                  <option key={area} value={area}>{area}</option>
                ))}
              </select>
            </div>

            <div>
              <label className="block text-sm font-medium mb-2">Organization Type</label>
              <select
                multiple
                className="w-full p-2 border border-gray-300 dark:border-gray-600 rounded-lg bg-white dark:bg-gray-800 max-h-32 overflow-y-auto"
                value={searchCriteria.organization_types}
                onChange={(e) => {
                  const values = Array.from(e.target.selectedOptions, option => option.value);
                  setSearchCriteria({ ...searchCriteria, organization_types: values });
                }}
              >
                {organizationTypes.map(type => (
                  <option key={type} value={type}>{type}</option>
                ))}
              </select>
            </div>
          </div>

          {/* Active Filters */}
          {(searchCriteria.countries.length > 0 || searchCriteria.expertise_areas.length > 0 || searchCriteria.organization_types.length > 0) && (
            <div className="flex flex-wrap gap-2 pt-2 border-t">
              {searchCriteria.countries.map(country => (
                <Badge key={country} variant="outline" className="cursor-pointer hover:bg-red-50"
                       onClick={() => setSearchCriteria({
                         ...searchCriteria,
                         countries: searchCriteria.countries.filter(c => c !== country)
                       })}>
                  <MapPin className="h-3 w-3 mr-1" />
                  {country} ×
                </Badge>
              ))}
              {searchCriteria.expertise_areas.map(area => (
                <Badge key={area} variant="outline" className="cursor-pointer hover:bg-red-50"
                       onClick={() => setSearchCriteria({
                         ...searchCriteria,
                         expertise_areas: searchCriteria.expertise_areas.filter(a => a !== area)
                       })}>
                  {area} ×
                </Badge>
              ))}
              {searchCriteria.organization_types.map(type => (
                <Badge key={type} variant="outline" className="cursor-pointer hover:bg-red-50"
                       onClick={() => setSearchCriteria({
                         ...searchCriteria,
                         organization_types: searchCriteria.organization_types.filter(t => t !== type)
                       })}>
                  <Building className="h-3 w-3 mr-1" />
                  {type} ×
                </Badge>
              ))}
            </div>
          )}
        </div>
      </Card>

      {/* Results */}
      <div className="grid grid-cols-1 lg:grid-cols-2 xl:grid-cols-3 gap-6">
        {filteredPartners.map((partner) => (
          <Card 
            key={partner.id} 
            className="p-6 hover:shadow-lg transition-all cursor-pointer"
            onClick={() => setSelectedPartner(partner)}
          >
            <div className="space-y-4">
              <div className="flex justify-between items-start">
                <div className="flex-1 min-w-0">
                  <div className="flex items-center gap-2 mb-1">
                    <h3 className="text-lg font-semibold text-gray-900 dark:text-gray-100 truncate">
                      {partner.name}
                    </h3>
                    {partner.verified && (
                      <Badge className="bg-green-100 text-green-800 dark:bg-green-900 dark:text-green-300 text-xs">
                        Verified
                      </Badge>
                    )}
                  </div>
                  
                  <div className="flex items-center gap-2 text-sm text-gray-600 dark:text-gray-400">
                    <MapPin className="h-4 w-4" />
                    <span>{partner.country}</span>
                  </div>
                </div>
                
                <div className="text-right">
                  <div className={`text-2xl font-bold ${getScoreColor(partner.compatibility_score)}`}>
                    {partner.compatibility_score}/10
                  </div>
                  <div className="flex items-center text-xs text-gray-500">
                    <Star className="h-3 w-3 mr-1" />
                    Match Score
                  </div>
                </div>
              </div>

              <div className="flex items-center gap-2">
                <Building className="h-4 w-4 text-gray-400" />
                <Badge className={getTypeColor(partner.organization_type)}>
                  {partner.organization_type}
                </Badge>
              </div>

              <div className="space-y-2">
                <div className="text-sm font-medium text-gray-700 dark:text-gray-300">
                  Expertise Areas:
                </div>
                <div className="flex flex-wrap gap-1">
                  {partner.expertise_areas.map((area) => (
                    <Badge key={area} variant="outline" className="text-xs">
                      {area}
                    </Badge>
                  ))}
                </div>
              </div>

              <p className="text-sm text-gray-600 dark:text-gray-400 line-clamp-2">
                {partner.partnership_rationale}
              </p>

              <div className="flex justify-between items-center text-sm text-gray-500">
                <div className="flex items-center gap-1">
                  <Mail className="h-3 w-3" />
                  <span>Contact available</span>
                </div>
                <span className="font-mono">{partner.erasmus_code}</span>
              </div>
            </div>
          </Card>
        ))}
      </div>

      {filteredPartners.length === 0 && !isSearching && (
        <Card className="p-12 text-center border-dashed">
          <Users className="h-16 w-16 text-gray-300 dark:text-gray-600 mx-auto mb-4" />
          <h3 className="text-lg font-semibold text-gray-500 dark:text-gray-400 mb-2">
            No partners found
          </h3>
          <p className="text-gray-400 dark:text-gray-500">
            Try adjusting your search criteria or explore different expertise areas.
          </p>
        </Card>
      )}

      {/* Partner Detail Modal */}
      {selectedPartner && (
        <div className="fixed inset-0 bg-black bg-opacity-50 flex items-center justify-center p-4 z-50">
          <Card className="max-w-2xl w-full max-h-[90vh] overflow-y-auto">
            <div className="p-6">
              <div className="flex justify-between items-start mb-6">
                <div>
                  <h2 className="text-2xl font-bold text-gray-900 dark:text-gray-100">
                    {selectedPartner.name}
                  </h2>
                  <div className="flex items-center gap-4 mt-2">
                    <div className="flex items-center gap-2">
                      <MapPin className="h-4 w-4" />
                      <span>{selectedPartner.country}</span>
                    </div>
                    <Badge className={getTypeColor(selectedPartner.organization_type)}>
                      {selectedPartner.organization_type}
                    </Badge>
                  </div>
                </div>
                <Button variant="outline" onClick={() => setSelectedPartner(null)}>
                  ×
                </Button>
              </div>

              <div className="space-y-6">
                <div>
                  <h3 className="font-semibold mb-2">Compatibility Score</h3>
                  <div className={`text-3xl font-bold ${getScoreColor(selectedPartner.compatibility_score)}`}>
                    {selectedPartner.compatibility_score}/10
                  </div>
                  <p className="text-sm text-gray-600 dark:text-gray-400 mt-1">
                    {selectedPartner.partnership_rationale}
                  </p>
                </div>

                <div>
                  <h3 className="font-semibold mb-2">Expertise Areas</h3>
                  <div className="flex flex-wrap gap-2">
                    {selectedPartner.expertise_areas.map((area) => (
                      <Badge key={area} variant="outline">
                        {area}
                      </Badge>
                    ))}
                  </div>
                </div>

                <div>
                  <h3 className="font-semibold mb-2">Contact Information</h3>
                  <div className="space-y-2">
                    <div className="flex items-center gap-2">
                      <Mail className="h-4 w-4" />
                      <a href={`mailto:${selectedPartner.contact_email}`} 
                         className="text-blue-500 hover:underline">
                        {selectedPartner.contact_email}
                      </a>
                    </div>
                    <div className="flex items-center gap-2">
                      <Globe className="h-4 w-4" />
                      <a href={selectedPartner.contact_website} 
                         target="_blank" 
                         rel="noopener noreferrer"
                         className="text-blue-500 hover:underline">
                        {selectedPartner.contact_website}
                      </a>
                    </div>
                    <div className="flex items-center gap-2 font-mono text-sm">
                      <Building className="h-4 w-4" />
                      <span>Erasmus Code: {selectedPartner.erasmus_code}</span>
                    </div>
                  </div>
                </div>

                <div className="flex gap-3">
                  <Button className="flex-1">
                    <Plus className="h-4 w-4 mr-2" />
                    Add to Project
                  </Button>
                  <Button variant="outline" className="flex-1">
                    <Mail className="h-4 w-4 mr-2" />
                    Contact Partner
                  </Button>
                </div>
              </div>
            </div>
          </Card>
        </div>
      )}
    </div>
  );
};