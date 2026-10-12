export interface RepoItem {
  name: string;
  html_url: string;
  description: string | null;
  language: string | null;
  homepage: string | null;
  updated_at: string;
  stargazers_count: number;
}

export interface ProfileData {
  activity_weeks: number[];
  data_note: string;
  events_available: boolean;
  followers: number;
  languages: Record<string, number>;
  languages_available: boolean;
  last_successful_refresh_utc: string;
  profile_available: boolean;
  public_push_event_count: number;
  public_repo_count: number;
  public_repo_stars: number;
  repos: RepoItem[];
  repos_available: boolean;
}

export interface VerifyResult {
  verified: boolean;
  checks: {
    check: string;
    status: 'pass' | 'fail' | 'warn';
    detail: string;
  }[];
}
