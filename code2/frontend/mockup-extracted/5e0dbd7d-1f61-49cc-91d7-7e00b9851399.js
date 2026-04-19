// Mock data for the Learning Analytics prototype.
// Numbers are plausible, not from the real API.

window.MOCK = (function () {
  const students = [
    { id: 'psyc2041', score: 0.71, level: 'Needs Help', submissions: 48, time: '1h 12m', retry: 0.42, recent: 0.68, trend: -0.12, feedback: 14 },
    { id: 'math1157', score: 0.58, level: 'Needs Help', submissions: 37, time: '54m',    retry: 0.35, recent: 0.61, trend: -0.08, feedback: 9  },
    { id: 'phys2023', score: 0.52, level: 'Needs Help', submissions: 29, time: '41m',    retry: 0.31, recent: 0.55, trend: -0.04, feedback: 7  },
    { id: 'biol1492', score: 0.46, level: 'Struggling', submissions: 42, time: '1h 03m', retry: 0.28, recent: 0.49, trend:  0.01, feedback: 5  },
    { id: 'chem3108', score: 0.41, level: 'Struggling', submissions: 33, time: '47m',    retry: 0.24, recent: 0.44, trend:  0.02, feedback: 4  },
    { id: 'cmps2211', score: 0.38, level: 'Struggling', submissions: 26, time: '38m',    retry: 0.22, recent: 0.40, trend:  0.00, feedback: 3  },
    { id: 'hist1024', score: 0.31, level: 'Minor Issues', submissions: 22, time: '32m',  retry: 0.18, recent: 0.33, trend:  0.04, feedback: 2  },
    { id: 'econ2260', score: 0.28, level: 'Minor Issues', submissions: 19, time: '28m',  retry: 0.15, recent: 0.29, trend:  0.05, feedback: 2  },
    { id: 'ling1805', score: 0.24, level: 'Minor Issues', submissions: 24, time: '34m',  retry: 0.12, recent: 0.22, trend:  0.07, feedback: 1  },
    { id: 'arts1009', score: 0.18, level: 'On Track',     submissions: 17, time: '24m',  retry: 0.09, recent: 0.16, trend:  0.09, feedback: 0  },
    { id: 'geog2414', score: 0.15, level: 'On Track',     submissions: 14, time: '21m',  retry: 0.08, recent: 0.13, trend:  0.10, feedback: 0  },
    { id: 'neur3077', score: 0.12, level: 'On Track',     submissions: 18, time: '26m',  retry: 0.06, recent: 0.11, trend:  0.11, feedback: 0  },
    { id: 'stat1622', score: 0.10, level: 'On Track',     submissions: 20, time: '28m',  retry: 0.05, recent: 0.08, trend:  0.12, feedback: 0  },
    { id: 'phil2190', score: 0.08, level: 'On Track',     submissions: 16, time: '22m',  retry: 0.04, recent: 0.07, trend:  0.13, feedback: 0  },
  ];

  const questions = [
    { id: 'Q-1407', level: 'Very Hard', score: 0.81, students: 34, avgAttempts: 4.2, avgTime: '3m 48s', firstFail: 0.78, module: 'Data Structures' },
    { id: 'Q-0928', level: 'Very Hard', score: 0.77, students: 41, avgAttempts: 3.9, avgTime: '3m 12s', firstFail: 0.74, module: 'Algorithms' },
    { id: 'Q-2311', level: 'Hard',      score: 0.68, students: 38, avgAttempts: 3.1, avgTime: '2m 44s', firstFail: 0.61, module: 'Data Structures' },
    { id: 'Q-0471', level: 'Hard',      score: 0.62, students: 29, avgAttempts: 2.8, avgTime: '2m 21s', firstFail: 0.55, module: 'Operating Systems' },
    { id: 'Q-1802', level: 'Hard',      score: 0.55, students: 35, avgAttempts: 2.5, avgTime: '2m 02s', firstFail: 0.48, module: 'Algorithms' },
    { id: 'Q-2045', level: 'Medium',    score: 0.46, students: 32, avgAttempts: 2.1, avgTime: '1m 41s', firstFail: 0.39, module: 'Algorithms' },
    { id: 'Q-0683', level: 'Medium',    score: 0.42, students: 28, avgAttempts: 1.9, avgTime: '1m 28s', firstFail: 0.35, module: 'Databases' },
    { id: 'Q-1551', level: 'Medium',    score: 0.37, students: 31, avgAttempts: 1.7, avgTime: '1m 14s', firstFail: 0.28, module: 'Databases' },
    { id: 'Q-0104', level: 'Easy',      score: 0.28, students: 26, avgAttempts: 1.3, avgTime: '0m 58s', firstFail: 0.21, module: 'Intro CS' },
    { id: 'Q-0219', level: 'Easy',      score: 0.21, students: 22, avgAttempts: 1.1, avgTime: '0m 47s', firstFail: 0.14, module: 'Intro CS' },
    { id: 'Q-0358', level: 'Easy',      score: 0.16, students: 19, avgAttempts: 1.0, avgTime: '0m 39s', firstFail: 0.09, module: 'Intro CS' },
  ];

  // 24 hourly buckets of submission counts across the day
  const timeline = [0,0,0,0,0,0,0,1,3,7,14,22,31,38,44,49,52,47,39,26,18,9,4,1];

  const assistants = [
    { id: 'a1', name: 'Amelia R.',  status: 'helping',  student: 'psyc2041', joined: '17:05' },
    { id: 'a2', name: 'Dev K.',     status: 'helping',  student: 'math1157', joined: '17:07' },
    { id: 'a3', name: 'Noor H.',    status: 'waiting',  student: null,       joined: '17:12' },
    { id: 'a4', name: 'Sam O.',     status: 'waiting',  student: null,       joined: '17:18' },
  ];

  const clusters = [
    { label: 'Off-by-one in loop bound',          share: 0.38, examples: ['for i in range(n): ...', 'while i <= len(arr):', 'range(1, n) instead of range(n+1)'] },
    { label: 'Confuses list mutation with return',share: 0.24, examples: ['arr.sort() — returns None', 'print(arr.reverse())', 'x = list.append(3)'] },
    { label: 'Treats dict as ordered by keys',    share: 0.21, examples: ['iterating expecting sorted', 'assumes insertion = sorted', 'no explicit sorted()'] },
    { label: 'Misses edge case: empty input',     share: 0.17, examples: ['crash on [] input', 'IndexError on arr[0]', 'no guard for n == 0'] },
  ];

  const submissions = [
    { t: '17:41', q: 'Q-1407', a: 'for i in range(1, n): total += arr[i]', score: 0.82 },
    { t: '17:38', q: 'Q-1407', a: 'for i in range(n+1): ...',              score: 0.74 },
    { t: '17:34', q: 'Q-0928', a: 'return arr.sort()',                     score: 0.91 },
    { t: '17:29', q: 'Q-0928', a: 'sorted(arr, reverse=false)',            score: 0.68 },
    { t: '17:22', q: 'Q-2311', a: 'if n == 0: pass',                       score: 0.55 },
    { t: '17:17', q: 'Q-0471', a: 'return list(set(arr))',                 score: 0.12 },
    { t: '17:11', q: 'Q-0471', a: 'return arr',                            score: 0.88 },
    { t: '17:05', q: 'Q-1802', a: 'dp[i] = dp[i-1] + 1',                   score: 0.21 },
  ];

  return { students, questions, timeline, assistants, clusters, submissions };
})();
