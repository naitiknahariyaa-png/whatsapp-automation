// NEXUS Platform - GitHub Connector
import { Octokit } from '@octokit/rest';
import { EventEmitter } from 'events';
import type { PullRequest, Issue, GitHubRepo, Message } from '../types/index.js';

interface GitHubConfig {
  token: string;
  onPR?: (pr: PullRequest) => void;
  onIssue?: (issue: Issue) => void;
  onError?: (error: Error) => void;
}

interface RepoConfig {
  owner: string;
  repo: string;
}

export class GitHubConnector extends EventEmitter {
  private octokit: Octokit;
  private config: GitHubConfig;
  private watchedRepos: Set<string> = new Set();

  constructor(config: GitHubConfig) {
    super();
    this.config = config;
    this.octokit = new Octokit({ auth: config.token });
  }

  private repoKey(owner: string, repo: string): string {
    return `${owner}/${repo}`;
  }

  async watchRepo(owner: string, repo: string): Promise<void> {
    const key = this.repoKey(owner, repo);
    this.watchedRepos.add(key);
    console.log(`Watching repo: ${key}`);
  }

  async unwatchRepo(owner: string, repo: string): Promise<void> {
    const key = this.repoKey(owner, repo);
    this.watchedRepos.delete(key);
  }

  async getPullRequests(owner: string, repo: string, state: 'open' | 'closed' | 'all' = 'open'): Promise<PullRequest[]> {
    try {
      const { data: prs } = await this.octokit.pulls.list({
        owner,
        repo,
        state,
        per_page: 30,
      });

      return prs.map((pr) => ({
        number: pr.number,
        title: pr.title,
        state: pr.state === 'open' ? 'open' : 'closed',
        author: pr.user?.login || 'unknown',
        repository: { owner, repo, fullName: `${owner}/${repo}` },
        createdAt: new Date(pr.created_at),
        updatedAt: new Date(pr.updated_at),
      }));
    } catch (error) {
      this.config.onError?.(error as Error);
      throw error;
    }
  }

  async getIssues(owner: string, repo: string, state: 'open' | 'closed' | 'all' = 'open'): Promise<Issue[]> {
    try {
      const { data: issues } = await this.octokit.issues.listForRepo({
        owner,
        repo,
        state,
        per_page: 30,
      });

      return issues
        .filter((issue) => !issue.pull_request) // Filter out PRs
        .map((issue) => ({
          number: issue.number,
          title: issue.title,
          body: issue.body || '',
          state: issue.state === 'open' ? 'open' : 'closed',
          author: issue.user?.login || 'unknown',
          labels: issue.labels.map((l) => l.name),
          repository: { owner, repo, fullName: `${owner}/${repo}` },
          createdAt: new Date(issue.created_at),
        }));
    } catch (error) {
      this.config.onError?.(error as Error);
      throw error;
    }
  }

  async createIssue(owner: string, repo: string, title: string, body: string): Promise<Issue> {
    const { data: issue } = await this.octokit.issues.create({
      owner,
      repo,
      title,
      body,
    });

    return {
      number: issue.number,
      title: issue.title,
      body: issue.body || '',
      state: issue.state as 'open' | 'closed',
      author: issue.user?.login || 'unknown',
      labels: issue.labels.map((l) => l.name),
      repository: { owner, repo, fullName: `${owner}/${repo}` },
      createdAt: new Date(issue.created_at),
    };
  }

  async commentOnPR(owner: string, repo: string, prNumber: number, comment: string): Promise<void> {
    await this.octokit.issues.createComment({
      owner,
      repo,
      issue_number: prNumber,
      body: comment,
    });
  }

  async mergePR(owner: string, repo: string, prNumber: number): Promise<void> {
    await this.octokit.pulls.merge({
      owner,
      repo,
      pull_number: prNumber,
    });
  }

  async addLabels(owner: string, repo: string, issueNumber: number, labels: string[]): Promise<void> {
    await this.octokit.issues.addLabels({
      owner,
      repo,
      issue_number: issueNumber,
      labels,
    });
  }

  async assignPR(owner: string, repo: string, prNumber: number, assignees: string[]): Promise<void> {
    await this.octokit.issues.addAssignees({
      owner,
      repo,
      issue_number: prNumber,
      assignees,
    });
  }

  async getFileContent(owner: string, repo: string, path: string, ref?: string): Promise<string> {
    const { data } = await this.octokit.repos.getContent({
      owner,
      repo,
      path,
      ref,
    });

    if ('content' in data) {
      return Buffer.from(data.content, 'base64').toString();
    }
    throw new Error('Not a file');
  }

  async reviewPR(owner: string, repo: string, prNumber: number): Promise<string> {
    const { data: pr } = await this.octokit.pulls.get({
      owner,
      repo,
      pull_number: prNumber,
    });

    const { data: files } = await this.octokit.pulls.listFiles({
      owner,
      repo,
      pull_number: prNumber,
    });

    let review = `# PR #${prNumber}: ${pr.title}\n\n`;
    review += `**Author:** @${pr.user?.login}\n`;
    review += `**Files Changed:** ${files.length}\n\n`;
    review += `## Changed Files:\n`;
    
    for (const file of files.slice(0, 10)) {
      review += `- \`${file.filename}\` (${file.changes} changes)\n`;
    }

    return review;
  }

  getWatchedRepos(): string[] {
    return Array.from(this.watchedRepos);
  }
}

export default GitHubConnector;
