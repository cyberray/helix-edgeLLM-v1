import { render, screen } from '@testing-library/react';
import userEvent from '@testing-library/user-event';
import { vi } from 'vitest';
import LLMEdgeSystem from '../../llm-edge-system.jsx';

describe('LLMEdgeSystem', () => {
  test('renders the main heading and top-level stats', () => {
    render(<LLMEdgeSystem />);

    expect(
      screen.getByRole('heading', { name: 'Edge LLM Architect' })
    ).toBeInTheDocument();
    expect(
      screen.getByText('Free LLMs for Mobile & Edge Deployment')
    ).toBeInTheDocument();
    expect(screen.getByText('4 Local Models')).toBeInTheDocument();
    expect(screen.getByText('4 Cloud APIs')).toBeInTheDocument();
  });

  test('filters model cards to local/edge models', async () => {
    const user = userEvent.setup();
    render(<LLMEdgeSystem />);

    await user.click(screen.getByRole('button', { name: 'Local/Edge' }));

    expect(screen.getByRole('heading', { name: 'Phi-3.5-mini' })).toBeInTheDocument();
    expect(screen.getByRole('heading', { name: 'Qwen2.5 3B' })).toBeInTheDocument();
    expect(screen.queryByRole('heading', { name: 'Gemini 1.5 Flash' })).not.toBeInTheDocument();
    expect(screen.queryByRole('heading', { name: 'Llama 3.1 70B (Groq)' })).not.toBeInTheDocument();
  });

  test('expands model details when clicking more info', async () => {
    const user = userEvent.setup();
    render(<LLMEdgeSystem />);

    const expandButtons = screen.getAllByRole('button', { name: /More Info/i });
    await user.click(expandButtons[0]);

    expect(screen.getByText('Use Cases')).toBeInTheDocument();
    expect(screen.getByText('Frameworks')).toBeInTheDocument();
  });

  test('runs routing playground and shows backend results', async () => {
    const user = userEvent.setup();

    const fetchMock = vi
      .fn()
      .mockResolvedValueOnce({
        ok: true,
        json: async () => ({
          selected_model: 'groq-llama',
          tier: 'cloud_fast',
          reason: 'Task requires deep reasoning',
          estimated_latency_ms: 200,
        }),
      })
      .mockResolvedValueOnce({
        ok: true,
        json: async () => ({
          response: 'AI can accelerate repetitive coding tasks and improve delivery speed.',
        }),
      });

    vi.stubGlobal('fetch', fetchMock);

    render(<LLMEdgeSystem />);

    await user.type(
      screen.getByPlaceholderText('Type a prompt to test routing...'),
      'Analyze AI impact on software development.'
    );

    await user.click(screen.getByRole('button', { name: 'Run Routing Test' }));

    expect(await screen.findByText(/Model:/)).toBeInTheDocument();
    expect(screen.getByText('groq-llama')).toBeInTheDocument();
    expect(screen.getByText('cloud_fast')).toBeInTheDocument();
    expect(screen.getByText('Task requires deep reasoning')).toBeInTheDocument();
    expect(
      screen.getByText(/AI can accelerate repetitive coding tasks and improve delivery speed\./)
    ).toBeInTheDocument();

    expect(fetchMock).toHaveBeenCalledTimes(2);
    expect(fetchMock).toHaveBeenNthCalledWith(
      1,
      '/api/route',
      expect.objectContaining({ method: 'POST' })
    );
    expect(fetchMock).toHaveBeenNthCalledWith(
      2,
      '/api/generate',
      expect.objectContaining({ method: 'POST' })
    );

    vi.unstubAllGlobals();
  });
});
