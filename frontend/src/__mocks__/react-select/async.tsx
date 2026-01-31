import React from 'react';

type Props = {
  placeholder?: string;
};

export default function AsyncSelect(props: Props) {
  return <input aria-label={props.placeholder ?? 'AsyncSelect'} />;
}
