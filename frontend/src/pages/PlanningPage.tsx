import React, { useState, useEffect } from 'react';
import { Card } from '../components/ui/Card';
import { Button } from '../components/ui/Button';
import { Input } from '../components/ui/Input';
import { Badge } from '../components/ui/Badge';
import { FileText, Calendar, Euro, MapPin, Users, Plus, Save, CheckCircle } from 'lucide-react';

interface ProjectPlan {
  id: string;
  title: string;
  description: string;
  duration_months: number;
  budget_estimate_eur: number;
  countries_involved: string[];
  objectives: string[];
  activities: Activity[];
  target_groups: string[];
  expected_outcomes: string[];
  created_at: string;
  status: 'draft' | 'review' | 'final';
}

interface Activity {
  id: string;
  title: string;
  description: string;
  month_start: number;
  month_end: number;
  responsible_partner: string;
}

export const PlanningPage: React.FC = () => {
  const [plans, setPlans] = useState<ProjectPlan[]>([]);
  const [selectedPlan, setSelectedPlan] = useState<ProjectPlan | null>(null);
  const [isEditing, setIsEditing] = useState(false);
  const [newActivity, setNewActivity] = useState<Partial<Activity>>({
    title: '',
    description: '',
    month_start: 1,
    month_end: 1,
    responsible_partner: ''
  });

  useEffect(() => {
    // Load existing plans from localStorage
    const saved = localStorage.getItem('project_plans');
    if (saved) {
      const loadedPlans = JSON.parse(saved);
      setPlans(loadedPlans);
      if (loadedPlans.length > 0) {
        setSelectedPlan(loadedPlans[0]);
      }
    }
  }, []);

  const savePlans = (updatedPlans: ProjectPlan[]) => {
    localStorage.setItem('project_plans', JSON.stringify(updatedPlans));
    setPlans(updatedPlans);
  };

  const createNewPlan = () => {
    const newPlan: ProjectPlan = {
      id: Date.now().toString(),
      title: 'New Erasmus+ Project',
      description: '',
      duration_months: 24,
      budget_estimate_eur: 300000,
      countries_involved: ['Sweden'],
      objectives: [],
      activities: [],
      target_groups: [],
      expected_outcomes: [],
      created_at: new Date().toISOString(),
      status: 'draft'
    };
    
    const updatedPlans = [...plans, newPlan];
    savePlans(updatedPlans);
    setSelectedPlan(newPlan);
    setIsEditing(true);
  };

  const updateSelectedPlan = (updates: Partial<ProjectPlan>) => {
    if (!selectedPlan) return;
    
    const updatedPlan = { ...selectedPlan, ...updates };
    const updatedPlans = plans.map(p => p.id === selectedPlan.id ? updatedPlan : p);
    savePlans(updatedPlans);
    setSelectedPlan(updatedPlan);
  };

  const addActivity = () => {
    if (!selectedPlan || !newActivity.title) return;
    
    const activity: Activity = {
      id: Date.now().toString(),
      title: newActivity.title!,
      description: newActivity.description || '',
      month_start: newActivity.month_start || 1,
      month_end: newActivity.month_end || 1,
      responsible_partner: newActivity.responsible_partner || ''
    };
    
    updateSelectedPlan({
      activities: [...selectedPlan.activities, activity]
    });
    
    setNewActivity({
      title: '',
      description: '',
      month_start: 1,
      month_end: 1,
      responsible_partner: ''
    });
  };

  const addListItem = (field: keyof ProjectPlan, value: string) => {
    if (!selectedPlan || !value.trim()) return;
    
    const currentList = selectedPlan[field] as string[];
    if (currentList.includes(value.trim())) return;
    
    updateSelectedPlan({
      [field]: [...currentList, value.trim()]
    });
  };

  const removeListItem = (field: keyof ProjectPlan, index: number) => {
    if (!selectedPlan) return;
    
    const currentList = selectedPlan[field] as string[];
    const newList = currentList.filter((_, i) => i !== index);
    
    updateSelectedPlan({
      [field]: newList
    });
  };

  const getStatusColor = (status: string) => {
    switch (status) {
      case 'draft': return 'bg-yellow-100 text-yellow-800 dark:bg-yellow-900 dark:text-yellow-300';
      case 'review': return 'bg-blue-100 text-blue-800 dark:bg-blue-900 dark:text-blue-300';
      case 'final': return 'bg-green-100 text-green-800 dark:bg-green-900 dark:text-green-300';
      default: return 'bg-gray-100 text-gray-800 dark:bg-gray-900 dark:text-gray-300';
    }
  };

  return (
    <div className="space-y-6">
      <div className="flex justify-between items-center">
        <div>
          <h1 className="text-3xl font-bold text-gray-900 dark:text-gray-100 flex items-center gap-3">
            <FileText className="h-8 w-8 text-blue-500" />
            Project Planning
          </h1>
          <p className="text-gray-600 dark:text-gray-400 mt-2">
            Develop detailed project plans for your Erasmus+ applications
          </p>
        </div>
        
        <Button onClick={createNewPlan} className="bg-blue-500 hover:bg-blue-600">
          <Plus className="h-4 w-4 mr-2" />
          New Plan
        </Button>
      </div>

      <div className="grid grid-cols-12 gap-6">
        {/* Plans List */}
        <div className="col-span-12 lg:col-span-4">
          <Card className="p-4">
            <h3 className="font-semibold mb-4">Project Plans</h3>
            <div className="space-y-2">
              {plans.map((plan) => (
                <div
                  key={plan.id}
                  className={`p-3 rounded-lg cursor-pointer transition-colors ${
                    selectedPlan?.id === plan.id
                      ? 'bg-blue-50 dark:bg-blue-900/30 border border-blue-200 dark:border-blue-700'
                      : 'hover:bg-gray-50 dark:hover:bg-gray-800'
                  }`}
                  onClick={() => setSelectedPlan(plan)}
                >
                  <div className="flex justify-between items-start">
                    <div className="flex-1 min-w-0">
                      <h4 className="font-medium text-sm truncate">{plan.title}</h4>
                      <div className="flex items-center gap-2 mt-1">
                        <Badge className={`text-xs ${getStatusColor(plan.status)}`}>
                          {plan.status}
                        </Badge>
                        <span className="text-xs text-gray-500">{plan.duration_months}m</span>
                      </div>
                    </div>
                  </div>
                </div>
              ))}
              
              {plans.length === 0 && (
                <div className="text-center py-8 text-gray-500 dark:text-gray-400">
                  <FileText className="h-12 w-12 mx-auto mb-3 opacity-50" />
                  <p>No plans yet</p>
                  <p className="text-sm">Create your first project plan</p>
                </div>
              )}
            </div>
          </Card>
        </div>

        {/* Plan Details */}
        <div className="col-span-12 lg:col-span-8">
          {selectedPlan ? (
            <div className="space-y-6">
              {/* Basic Info */}
              <Card className="p-6">
                <div className="flex justify-between items-start mb-4">
                  <h3 className="text-xl font-semibold">Project Overview</h3>
                  <div className="flex gap-2">
                    <Button
                      variant="outline"
                      size="sm"
                      onClick={() => setIsEditing(!isEditing)}
                    >
                      {isEditing ? 'Save' : 'Edit'}
                    </Button>
                    <Badge className={getStatusColor(selectedPlan.status)}>
                      {selectedPlan.status}
                    </Badge>
                  </div>
                </div>

                <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
                  <div>
                    <label className="block text-sm font-medium mb-2">Project Title</label>
                    {isEditing ? (
                      <Input
                        value={selectedPlan.title}
                        onChange={(e) => updateSelectedPlan({ title: e.target.value })}
                      />
                    ) : (
                      <p className="p-2 bg-gray-50 dark:bg-gray-800 rounded">{selectedPlan.title}</p>
                    )}
                  </div>
                  
                  <div>
                    <label className="block text-sm font-medium mb-2">Duration (months)</label>
                    {isEditing ? (
                      <Input
                        type="number"
                        min="3"
                        max="36"
                        value={selectedPlan.duration_months}
                        onChange={(e) => updateSelectedPlan({ duration_months: parseInt(e.target.value) })}
                      />
                    ) : (
                      <p className="p-2 bg-gray-50 dark:bg-gray-800 rounded flex items-center gap-2">
                        <Calendar className="h-4 w-4" />
                        {selectedPlan.duration_months} months
                      </p>
                    )}
                  </div>

                  <div>
                    <label className="block text-sm font-medium mb-2">Budget Estimate (EUR)</label>
                    {isEditing ? (
                      <Input
                        type="number"
                        min="0"
                        value={selectedPlan.budget_estimate_eur}
                        onChange={(e) => updateSelectedPlan({ budget_estimate_eur: parseInt(e.target.value) })}
                      />
                    ) : (
                      <p className="p-2 bg-gray-50 dark:bg-gray-800 rounded flex items-center gap-2">
                        <Euro className="h-4 w-4" />
                        €{selectedPlan.budget_estimate_eur.toLocaleString()}
                      </p>
                    )}
                  </div>
                  
                  <div>
                    <label className="block text-sm font-medium mb-2">Status</label>
                    {isEditing ? (
                      <select
                        className="w-full p-2 border border-gray-300 dark:border-gray-600 rounded-lg bg-white dark:bg-gray-800"
                        value={selectedPlan.status}
                        onChange={(e) => updateSelectedPlan({ status: e.target.value as ProjectPlan['status'] })}
                      >
                        <option value="draft">Draft</option>
                        <option value="review">Under Review</option>
                        <option value="final">Final</option>
                      </select>
                    ) : (
                      <p className="p-2 bg-gray-50 dark:bg-gray-800 rounded flex items-center gap-2">
                        <CheckCircle className="h-4 w-4" />
                        {selectedPlan.status}
                      </p>
                    )}
                  </div>
                </div>

                <div className="mt-4">
                  <label className="block text-sm font-medium mb-2">Project Description</label>
                  {isEditing ? (
                    <textarea
                      className="w-full p-3 border border-gray-300 dark:border-gray-600 rounded-lg bg-white dark:bg-gray-800 resize-none"
                      rows={4}
                      value={selectedPlan.description}
                      onChange={(e) => updateSelectedPlan({ description: e.target.value })}
                    />
                  ) : (
                    <p className="p-3 bg-gray-50 dark:bg-gray-800 rounded min-h-[100px]">
                      {selectedPlan.description || 'No description yet...'}
                    </p>
                  )}
                </div>
              </Card>

              {/* Countries */}
              <Card className="p-6">
                <h3 className="text-lg font-semibold mb-4 flex items-center gap-2">
                  <MapPin className="h-5 w-5" />
                  Partner Countries
                </h3>
                
                <div className="flex flex-wrap gap-2 mb-4">
                  {selectedPlan.countries_involved.map((country, index) => (
                    <Badge 
                      key={index} 
                      variant="outline"
                      className={isEditing ? "cursor-pointer hover:bg-red-50 dark:hover:bg-red-900" : ""}
                      onClick={() => isEditing && removeListItem('countries_involved', index)}
                    >
                      {country} {isEditing && '×'}
                    </Badge>
                  ))}
                </div>
                
                {isEditing && (
                  <div className="flex gap-2">
                    <Input
                      placeholder="Add country..."
                      onKeyDown={(e) => {
                        if (e.key === 'Enter') {
                          addListItem('countries_involved', e.currentTarget.value);
                          e.currentTarget.value = '';
                        }
                      }}
                    />
                  </div>
                )}
              </Card>

              {/* Activities */}
              <Card className="p-6">
                <h3 className="text-lg font-semibold mb-4">Project Activities</h3>
                
                <div className="space-y-4">
                  {selectedPlan.activities.map((activity, index) => (
                    <div key={activity.id} className="p-4 border border-gray-200 dark:border-gray-700 rounded-lg">
                      <div className="flex justify-between items-start">
                        <div className="flex-1">
                          <h4 className="font-medium">{activity.title}</h4>
                          <p className="text-sm text-gray-600 dark:text-gray-400 mt-1">
                            {activity.description}
                          </p>
                          <div className="flex items-center gap-4 text-xs text-gray-500 mt-2">
                            <span>Months: {activity.month_start}-{activity.month_end}</span>
                            {activity.responsible_partner && (
                              <span>Partner: {activity.responsible_partner}</span>
                            )}
                          </div>
                        </div>
                      </div>
                    </div>
                  ))}
                </div>

                {isEditing && (
                  <div className="mt-6 p-4 border-2 border-dashed border-gray-300 dark:border-gray-600 rounded-lg">
                    <h4 className="font-medium mb-3">Add New Activity</h4>
                    <div className="grid grid-cols-1 md:grid-cols-2 gap-3">
                      <Input
                        placeholder="Activity title..."
                        value={newActivity.title}
                        onChange={(e) => setNewActivity({ ...newActivity, title: e.target.value })}
                      />
                      <Input
                        placeholder="Responsible partner..."
                        value={newActivity.responsible_partner}
                        onChange={(e) => setNewActivity({ ...newActivity, responsible_partner: e.target.value })}
                      />
                      <div className="flex gap-2">
                        <Input
                          type="number"
                          min="1"
                          max={selectedPlan.duration_months}
                          placeholder="Start month"
                          value={newActivity.month_start}
                          onChange={(e) => setNewActivity({ ...newActivity, month_start: parseInt(e.target.value) })}
                        />
                        <Input
                          type="number"
                          min="1"
                          max={selectedPlan.duration_months}
                          placeholder="End month"
                          value={newActivity.month_end}
                          onChange={(e) => setNewActivity({ ...newActivity, month_end: parseInt(e.target.value) })}
                        />
                      </div>
                      <textarea
                        className="md:col-span-2 p-2 border border-gray-300 dark:border-gray-600 rounded-lg bg-white dark:bg-gray-800 resize-none"
                        rows={2}
                        placeholder="Activity description..."
                        value={newActivity.description}
                        onChange={(e) => setNewActivity({ ...newActivity, description: e.target.value })}
                      />
                    </div>
                    <Button onClick={addActivity} className="mt-3" size="sm">
                      <Plus className="h-4 w-4 mr-1" />
                      Add Activity
                    </Button>
                  </div>
                )}
              </Card>
            </div>
          ) : (
            <Card className="p-12 text-center">
              <FileText className="h-16 w-16 text-gray-300 dark:text-gray-600 mx-auto mb-4" />
              <h3 className="text-lg font-semibold text-gray-500 dark:text-gray-400 mb-2">
                No plan selected
              </h3>
              <p className="text-gray-400 dark:text-gray-500">
                Select a plan from the list or create a new one to get started.
              </p>
            </Card>
          )}
        </div>
      </div>
    </div>
  );
};