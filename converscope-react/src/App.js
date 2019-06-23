import React from 'react';
import './App.css';

function ConversationPill(props) {
  return (
    <div className="card">
      <div className="card-body">
        <h5 className="">{props.group_name}</h5>
        <div className="">{props.message_count} messages</div>
      </div>
    </div>
  );
}

class ConversationList extends React.Component {
  constructor(props) {
    super(props);
    this.state = {
      error: null,
      isLoaded: false,
      items: []
    };
  }

  componentDidMount() {
    fetch("http://localhost:5000/api/conversations")
      .then(res => res.json())
      .then(
        (result) => {
          this.setState({
            isLoaded: true,
            items: result.conversations
          });
        },
        // Note: it's important to handle errors here
        // instead of a catch() block so that we don't swallow
        // exceptions from actual bugs in components.
        (error) => {
          this.setState({
            isLoaded: true,
            error
          });
        }
      )
  }

  render() {
    const { error, isLoaded, items } = this.state;
    if (error) {
      return <div>Error: {error.message}</div>;
    } else if (!isLoaded) {
      return <div>Loading...</div>;
    } else {
      return (
        <ul>
          {items.map(item => (
            <ConversationPill group_name={item.groupName} message_count={item.count} />
          ))}
        </ul>
      );
    }
  }
}

function App() {
  return (
    <div className="container-fluid">
      <header>
        <h1>Converscope</h1>
      </header>
      <div>
        <ConversationList />
      </div>
    </div>
  );
}

export default App;
