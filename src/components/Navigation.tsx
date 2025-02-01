import { Link } from "react-router-dom";
import { Button } from "./ui/button";
import { Home, Video, MessageCircle, Phone, User } from "lucide-react";

const Navigation = () => {
  return (
    <nav className="fixed bottom-0 left-0 right-0 bg-white border-t p-4 flex justify-around items-center">
      <Link to="/">
        <Button variant="ghost" size="icon">
          <Home className="h-6 w-6" />
        </Button>
      </Link>
      <Link to="/shorts">
        <Button variant="ghost" size="icon">
          <Video className="h-6 w-6" />
        </Button>
      </Link>
      <Link to="/chat">
        <Button variant="ghost" size="icon">
          <MessageCircle className="h-6 w-6" />
        </Button>
      </Link>
      <Link to="/calls">
        <Button variant="ghost" size="icon">
          <Phone className="h-6 w-6" />
        </Button>
      </Link>
      <Link to="/profile">
        <Button variant="ghost" size="icon">
          <User className="h-6 w-6" />
        </Button>
      </Link>
    </nav>
  );
};

export default Navigation;