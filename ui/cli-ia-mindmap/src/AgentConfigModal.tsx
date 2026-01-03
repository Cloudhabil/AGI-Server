import React, { useState } from 'react';

interface Props {
  onSubmit: (cfg: { name: string; bootTask: string }) => void;
  onCancel: () => void;
}

const overlayStyle: React.CSSProperties = {
  position: 'fixed',
  top: 0,
  left: 0,
  right: 0,
  bottom: 0,
  backgroundColor: 'rgba(0,0,0,0.5)',
  display: 'flex',
  alignItems: 'center',
  justifyContent: 'center',
  zIndex: 1000
};

const modalStyle: React.CSSProperties = {
  background: '#222',
  padding: '20px',
  borderRadius: '8px',
  color: '#fff',
  minWidth: '300px'
};

const AgentConfigModal: React.FC<Props> = ({ onSubmit, onCancel }) => {
  const [name, setName] = useState('');
  const [bootTask, setBootTask] = useState('');

  return (
    <div style={overlayStyle}>
      <div style={modalStyle}>
        <h3>Create Agent</h3>
        <input
          style={{ width: '100%', marginBottom: '10px' }}
          placeholder="Name"
          value={name}
          onChange={e => setName(e.target.value)}
        />
        <textarea
          style={{ width: '100%', height: '80px', marginBottom: '10px' }}
          placeholder="Boot Task"
          value={bootTask}
          onChange={e => setBootTask(e.target.value)}
        />
        <div style={{ display: 'flex', justifyContent: 'flex-end', gap: '10px' }}>
          <button onClick={() => onSubmit({ name, bootTask })}>Create</button>
          <button onClick={onCancel}>Cancel</button>
        </div>
      </div>
    </div>
  );
};

export default AgentConfigModal;
