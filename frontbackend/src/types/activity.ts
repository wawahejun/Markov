export interface Activity {
  id: string;
  title: string;
  description: string;
  image: string;
  category: string;
  date: string;
  location: string;
  participants: number;
  maxParticipants: number;
  tags: string[];
  interests: string[];
  isRecommended?: boolean;
  recommendationScore?: number;
  time?: string;
  duration?: string;
  organizer?: string;
  price?: number;
  difficulty?: 'Easy' | 'Medium' | 'Hard';
  rating?: number;
  reviews?: number;
}

export interface ActivityWithMeta extends Activity {
  metadata?: {
    parallaxType?: 'zoom' | 'scroll';
    animationDelay?: number;
  };
}

export interface CategorizedActivities {
  recommendedForYou: Activity[];
  trendingNow: Activity[];
  newThisWeek: Activity[];
  popularInYourArea: Activity[];
}
