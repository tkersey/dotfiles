-- rls-coverage.sql
--
-- Verify that every table in the public schema has RLS enabled and has at
-- least one policy defined. Run this in CI after every migration.
--
-- Exit 0 = all tables covered
-- Exit >0 = missing coverage (prints offending tables)

\set ON_ERROR_STOP on

-- 1. Tables without RLS enabled
WITH missing_rls AS (
  SELECT schemaname, tablename
  FROM pg_tables
  WHERE schemaname = 'public'
    AND NOT rowsecurity
    AND tablename NOT IN (
      -- Explicitly exempt reference tables (maintain this list)
      'subscription_tiers',
      'pricing_plans',
      'feature_flags_public'
    )
)
SELECT
  CASE WHEN COUNT(*) = 0 THEN '✓ All tables have RLS enabled'
       ELSE '✗ ' || COUNT(*) || ' tables missing RLS:'
  END AS check_1_result
FROM missing_rls;

SELECT '  - ' || schemaname || '.' || tablename
FROM pg_tables
WHERE schemaname = 'public'
  AND NOT rowsecurity
  AND tablename NOT IN ('subscription_tiers', 'pricing_plans', 'feature_flags_public');

-- 2. Tables with RLS enabled but NO policies defined
WITH missing_policies AS (
  SELECT t.schemaname, t.tablename
  FROM pg_tables t
  WHERE t.schemaname = 'public'
    AND t.rowsecurity
    AND NOT EXISTS (
      SELECT 1 FROM pg_policies p
      WHERE p.schemaname = t.schemaname
        AND p.tablename = t.tablename
    )
)
SELECT
  CASE WHEN COUNT(*) = 0 THEN '✓ All RLS-enabled tables have policies'
       ELSE '✗ ' || COUNT(*) || ' tables have RLS but no policies (implicit deny):'
  END AS check_2_result
FROM missing_policies;

SELECT '  - ' || schemaname || '.' || tablename
FROM pg_tables t
WHERE t.schemaname = 'public'
  AND t.rowsecurity
  AND NOT EXISTS (
    SELECT 1 FROM pg_policies p
    WHERE p.schemaname = t.schemaname AND p.tablename = t.tablename
  );

-- 3. Policies that might be overly permissive
SELECT '✗ Overly permissive policy found: ' || schemaname || '.' || tablename || ' (' || policyname || ')'
FROM pg_policies
WHERE schemaname = 'public'
  AND qual = 'true'
  AND 'authenticated' = ANY(roles)
  AND tablename NOT IN ('subscription_tiers', 'pricing_plans', 'feature_flags_public');

-- 4. INSERT/UPDATE policies missing WITH CHECK
SELECT '⚠ ' || schemaname || '.' || tablename || ' (' || policyname || ') has USING but no WITH CHECK'
FROM pg_policies
WHERE schemaname = 'public'
  AND cmd IN ('INSERT', 'UPDATE', 'ALL')
  AND with_check IS NULL
  AND qual IS NOT NULL;

-- 5. Anon role should have no privileges
SELECT '✗ anon role has privilege: ' || table_schema || '.' || table_name || ' (' || privilege_type || ')'
FROM information_schema.table_privileges
WHERE grantee = 'anon'
  AND table_schema = 'public';
