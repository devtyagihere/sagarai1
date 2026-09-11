const USERS_KEY = "freight_intelligence_users";
const CURRENT_USER_KEY = "freight_intelligence_current_user";

export function getUsers() {
  try {
    return JSON.parse(localStorage.getItem(USERS_KEY)) || [];
  } catch {
    return [];
  }
}

export function signupUser({ name, email, password }) {
  const users = getUsers();

  const normalizedEmail = email.trim().toLowerCase();

  const existingUser = users.find(
    (user) => user.email === normalizedEmail
  );

  if (existingUser) {
    throw new Error("An account with this email already exists.");
  }

  const newUser = {
    id: crypto.randomUUID(),
    name: name.trim(),
    email: normalizedEmail,
    password,
    createdAt: new Date().toISOString(),
  };

  localStorage.setItem(
    USERS_KEY,
    JSON.stringify([...users, newUser])
  );

  const safeUser = {
    id: newUser.id,
    name: newUser.name,
    email: newUser.email,
    createdAt: newUser.createdAt,
  };

  localStorage.setItem(
    CURRENT_USER_KEY,
    JSON.stringify(safeUser)
  );

  return safeUser;
}

export function loginUser({ email, password }) {
  const users = getUsers();

  const normalizedEmail = email.trim().toLowerCase();

  const user = users.find(
    (item) =>
      item.email === normalizedEmail &&
      item.password === password
  );

  if (!user) {
    throw new Error("Invalid email or password.");
  }

  const safeUser = {
    id: user.id,
    name: user.name,
    email: user.email,
    createdAt: user.createdAt,
  };

  localStorage.setItem(
    CURRENT_USER_KEY,
    JSON.stringify(safeUser)
  );

  return safeUser;
}

export function getCurrentUser() {
  try {
    return JSON.parse(
      localStorage.getItem(CURRENT_USER_KEY)
    );
  } catch {
    return null;
  }
}

export function logoutUser() {
  localStorage.removeItem(CURRENT_USER_KEY);
}

export function isAuthenticated() {
  return Boolean(getCurrentUser());
}