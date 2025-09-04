import React, { useState, useEffect } from 'react';
import { Card } from '../components/ui/Card';
import { Button } from '../components/ui/Button';
import { Input } from '../components/ui/Input';
import { Badge } from '../components/ui/Badge';
import { Lightbulb, Plus, Trash2, Save, Sparkles, Target, Users, Globe } from 'lucide-react';

interface BrainstormConcept {
  id: string;
  title: string;
  description: string;
  focus_area: string;
  target_audience: string;
  innovation_angle: string;
  tags: string[];
  created_at: string;
}

export const BrainstormingPage: React.FC = () => {
  const [concepts, setConcepts] = useState<BrainstormConcept[]>([]);
  const [newConcept, setNewConcept] = useState({
    title: '',
    description: '',
    focus_area: '',
    target_audience: '',
    innovation_angle: '',
    tags: [] as string[]
  });
  const [tagInput, setTagInput] = useState('');
  const [isGenerating, setIsGenerating] = useState(false);

  useEffect(() => {
    // Load existing concepts from localStorage for now
    const saved = localStorage.getItem('brainstorm_concepts');
    if (saved) {
      setConcepts(JSON.parse(saved));
    }
  }, []);

  const saveConcepts = (updatedConcepts: BrainstormConcept[]) => {
    localStorage.setItem('brainstorm_concepts', JSON.stringify(updatedConcepts));
    setConcepts(updatedConcepts);
  };

  const addConcept = () => {
    if (!newConcept.title.trim()) return;

    const concept: BrainstormConcept = {
      id: Date.now().toString(),
      ...newConcept,
      created_at: new Date().toISOString()
    };

    const updatedConcepts = [...concepts, concept];
    saveConcepts(updatedConcepts);
    
    // Reset form
    setNewConcept({
      title: '',
      description: '',
      focus_area: '',
      target_audience: '',
      innovation_angle: '',
      tags: []
    });
    setTagInput('');
  };

  const deleteConcept = (id: string) => {
    const updatedConcepts = concepts.filter(c => c.id !== id);
    saveConcepts(updatedConcepts);
  };

  const addTag = () => {
    if (tagInput.trim() && !newConcept.tags.includes(tagInput.trim())) {
      setNewConcept({
        ...newConcept,
        tags: [...newConcept.tags, tagInput.trim()]
      });
      setTagInput('');
    }
  };

  const removeTag = (tagToRemove: string) => {
    setNewConcept({
      ...newConcept,
      tags: newConcept.tags.filter(tag => tag !== tagToRemove)
    });
  };

  const generateIdeas = async () => {
    setIsGenerating(true);
    // Simulate AI-powered idea generation
    setTimeout(() => {
      const aiGeneratedConcepts = [
        {
          id: Date.now().toString(),
          title: "Digital Skills for Rural Youth",
          description: "Addressing the digital divide by providing comprehensive digital literacy training for young people in rural areas across Europe.",
          focus_area: "Digital Skills",
          target_audience: "Young people aged 16-25 in rural communities",
          innovation_angle: "Mobile learning labs and peer-to-peer teaching methodology",
          tags: ["digital-divide", "rural-development", "peer-learning"],
          created_at: new Date().toISOString()
        },
        {
          id: (Date.now() + 1).toString(),
          title: "Green Entrepreneurship Network",
          description: "Creating a European network of young entrepreneurs focused on sustainable business solutions and environmental innovation.",
          focus_area: "Environmental Sustainability",
          target_audience: "Young entrepreneurs and environmental activists",
          innovation_angle: "Cross-border incubator program with sustainability focus",
          tags: ["entrepreneurship", "sustainability", "networking"],
          created_at: new Date().toISOString()
        }
      ];
      
      const updatedConcepts = [...concepts, ...aiGeneratedConcepts];
      saveConcepts(updatedConcepts);
      setIsGenerating(false);
    }, 2000);
  };

  return (
    <div className="space-y-8">
      <div className="text-center space-y-4">
        <div className="flex items-center justify-center gap-3">
          <Lightbulb className="h-8 w-8 text-blue-500" />
          <h1 className="text-4xl font-bold bg-gradient-to-r from-blue-600 to-purple-600 dark:from-blue-400 dark:to-purple-400 bg-clip-text text-transparent">
            Erasmus+ Project Brainstorming
          </h1>
        </div>
        <p className="text-lg text-gray-600 dark:text-gray-400 max-w-2xl mx-auto">
          Generate innovative project ideas for Erasmus+ applications. Think about youth empowerment, 
          education, inclusion, and European cooperation.
        </p>
        
        <Button 
          onClick={generateIdeas} 
          disabled={isGenerating}
          className="bg-gradient-to-r from-purple-500 to-pink-500 hover:from-purple-600 hover:to-pink-600"
        >
          <Sparkles className="h-4 w-4 mr-2" />
          {isGenerating ? 'Generating Ideas...' : 'Generate AI Ideas'}
        </Button>
      </div>

      {/* Add New Concept Form */}
      <Card className="p-6 border-dashed border-2 border-gray-300 dark:border-gray-600">
        <div className="space-y-4">
          <div className="flex items-center gap-2 mb-4">
            <Plus className="h-5 w-5 text-blue-500" />
            <h3 className="text-lg font-semibold">Add New Project Concept</h3>
          </div>
          
          <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
            <Input
              placeholder="Project title..."
              value={newConcept.title}
              onChange={(e) => setNewConcept({ ...newConcept, title: e.target.value })}
            />
            <Input
              placeholder="Focus area (e.g., Digital Skills, Environment)..."
              value={newConcept.focus_area}
              onChange={(e) => setNewConcept({ ...newConcept, focus_area: e.target.value })}
            />
          </div>
          
          <textarea
            className="w-full p-3 border border-gray-300 dark:border-gray-600 rounded-lg bg-white dark:bg-gray-800 text-gray-900 dark:text-gray-100 resize-none"
            rows={3}
            placeholder="Project description..."
            value={newConcept.description}
            onChange={(e) => setNewConcept({ ...newConcept, description: e.target.value })}
          />
          
          <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
            <Input
              placeholder="Target audience..."
              value={newConcept.target_audience}
              onChange={(e) => setNewConcept({ ...newConcept, target_audience: e.target.value })}
            />
            <Input
              placeholder="Innovation angle..."
              value={newConcept.innovation_angle}
              onChange={(e) => setNewConcept({ ...newConcept, innovation_angle: e.target.value })}
            />
          </div>
          
          <div className="flex gap-2">
            <Input
              placeholder="Add tags..."
              value={tagInput}
              onChange={(e) => setTagInput(e.target.value)}
              onKeyDown={(e) => e.key === 'Enter' && (e.preventDefault(), addTag())}
            />
            <Button onClick={addTag} variant="outline">Add Tag</Button>
          </div>
          
          {newConcept.tags.length > 0 && (
            <div className="flex flex-wrap gap-2">
              {newConcept.tags.map((tag) => (
                <Badge 
                  key={tag} 
                  variant="secondary" 
                  className="cursor-pointer hover:bg-red-100 dark:hover:bg-red-900"
                  onClick={() => removeTag(tag)}
                >
                  {tag} ×
                </Badge>
              ))}
            </div>
          )}
          
          <Button onClick={addConcept} className="w-full">
            <Save className="h-4 w-4 mr-2" />
            Save Concept
          </Button>
        </div>
      </Card>

      {/* Existing Concepts */}
      <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
        {concepts.map((concept) => (
          <Card key={concept.id} className="p-6 hover:shadow-lg transition-shadow">
            <div className="space-y-4">
              <div className="flex justify-between items-start">
                <h3 className="text-xl font-semibold text-gray-900 dark:text-gray-100">
                  {concept.title}
                </h3>
                <Button
                  variant="outline"
                  size="sm"
                  onClick={() => deleteConcept(concept.id)}
                  className="text-red-500 hover:text-red-700"
                >
                  <Trash2 className="h-4 w-4" />
                </Button>
              </div>
              
              <p className="text-gray-600 dark:text-gray-400">
                {concept.description}
              </p>
              
              <div className="space-y-2">
                <div className="flex items-center gap-2 text-sm">
                  <Target className="h-4 w-4 text-blue-500" />
                  <span className="font-medium">Focus:</span>
                  <span>{concept.focus_area}</span>
                </div>
                <div className="flex items-center gap-2 text-sm">
                  <Users className="h-4 w-4 text-green-500" />
                  <span className="font-medium">Audience:</span>
                  <span>{concept.target_audience}</span>
                </div>
                <div className="flex items-center gap-2 text-sm">
                  <Globe className="h-4 w-4 text-purple-500" />
                  <span className="font-medium">Innovation:</span>
                  <span>{concept.innovation_angle}</span>
                </div>
              </div>
              
              {concept.tags.length > 0 && (
                <div className="flex flex-wrap gap-2">
                  {concept.tags.map((tag) => (
                    <Badge key={tag} variant="outline" className="text-xs">
                      {tag}
                    </Badge>
                  ))}
                </div>
              )}
              
              <div className="text-xs text-gray-500 dark:text-gray-400 pt-2 border-t">
                Created: {new Date(concept.created_at).toLocaleDateString()}
              </div>
            </div>
          </Card>
        ))}
      </div>
      
      {concepts.length === 0 && !isGenerating && (
        <Card className="p-12 text-center border-dashed">
          <Lightbulb className="h-16 w-16 text-gray-300 dark:text-gray-600 mx-auto mb-4" />
          <h3 className="text-lg font-semibold text-gray-500 dark:text-gray-400 mb-2">
            No project concepts yet
          </h3>
          <p className="text-gray-400 dark:text-gray-500">
            Start brainstorming your first Erasmus+ project idea above, or use AI to generate suggestions.
          </p>
        </Card>
      )}
    </div>
  );
};