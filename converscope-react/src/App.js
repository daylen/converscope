import React from 'react';
import './App.css';

function ConversationPill(props) {
  return (
    <div className="card mb-3">
      <div className="card-body">
        <h5 className="">{props.group_name}</h5>
        <div className="">{props.message_count} messages</div>
        <div className="text-muted small"><ul className="participants">{props.participants ? props.participants.map((name) => <li>{name}</li>) : "No participants"}</ul></div>
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
      return (
        <div class="text-center">
          <div class="spinner-border" role="status">
            <span class="sr-only">Loading...</span>
          </div>
        </div>
      );
    } else {
      return (
          items.map(item => (
            <ConversationPill group_name={item.groupName} message_count={item.count} participants={item.participant} />
          ))
      );
    }
  }
}

function App() {
  return (
    <div>
    <nav class="navbar navbar-dark bg-dark mb-3">
    <div className="container">
      <span class="navbar-brand mb-0 h1">Converscope</span>
      </div>
    </nav>
    <div className="container">
      <div className="row">
        <div className="col-3">
        Filters would go here
        </div>
        <div className="col-9">
        <ConversationList />
        </div>
      </div>
    </div>
    </div>
  );
}

export default App;
